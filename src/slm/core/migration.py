"""Directory migration primitives and safety helpers."""

from __future__ import annotations

import os
import shutil
import time
from pathlib import Path
from typing import Iterable, List, Optional

from .scanner import SymlinkInfo

class MigrationError(RuntimeError):
    pass


def _safe_move_dir(old: Path, new: Path) -> None:
    """Safe directory move; auto-creates parent directories; cross-device fallback."""

    if new.exists():
        raise MigrationError(f"Destination exists: {new}")

    try:
        new.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise MigrationError(f"Cannot create parent directory {new.parent}: {e}") from e

    try:
        old.rename(new)
    except OSError as e:
        if getattr(e, "errno", None) == 18 or "cross-device" in str(e).lower():
            shutil.copytree(old, new)
            shutil.rmtree(old)
        else:
            raise


def _derive_backup_path(target: Path, now: Optional[float] = None) -> Path:
    timestamp = time.strftime("%Y%m%d-%H%M%S", time.localtime(now or time.time()))
    base = target.with_name(f"{target.name}~{timestamp}")
    candidate = base
    counter = 1
    while candidate.exists():
        candidate = target.with_name(f"{target.name}~{timestamp}-{counter}")
        counter += 1
    return candidate


def _retarget_symlink(link: Path, new_target: Path, *, make_relative: bool) -> None:
    if not link.is_symlink():
        raise MigrationError(f"Not a symlink: {link}")
    link.unlink()
    target_for_link = str(new_target)
    if make_relative:
        try:
            target_for_link = os.path.relpath(str(new_target), start=str(link.parent))
        except Exception:
            target_for_link = str(new_target)
    os.symlink(target_for_link, str(link))


def migrate_target_and_update_links(
    current_target: Path,
    new_target: Path,
    links: Iterable[Path],
    dry_run: bool = True,
    conflict_strategy: str = "abort",
    backup_path: Optional[Path] = None,
    data_root: Optional[Path] = None,
    link_mode: str = "relative",
) -> List[str]:
    actions: List[str] = []
    current_target = current_target.resolve()
    new_target = new_target.expanduser()
    links_list = list(links)

    valid_modes = {"relative", "absolute", "inline"}
    if link_mode not in valid_modes:
        raise MigrationError(f"Invalid link_mode: {link_mode}")
    use_relative_links = link_mode == "relative"
    materialize_links = link_mode == "inline"

    if not new_target.is_absolute():
        if data_root:
            new_target = (Path(data_root).resolve() / new_target).resolve()
        else:
            new_target = new_target.resolve()
    else:
        new_target = new_target.resolve()

    if current_target == new_target:
        raise MigrationError("New target equals current target.")
    try:
        current_target.relative_to("/")
        new_target.relative_to("/")
    except Exception:
        pass
    if str(new_target).startswith(str(current_target) + os.sep):
        raise MigrationError("New target cannot be inside current target.")

    backup_in_use: Optional[Path] = None
    if new_target.exists():
        if conflict_strategy == "abort":
            raise MigrationError(f"Destination exists: {new_target}")
        if conflict_strategy != "backup":
            raise MigrationError(f"Unsupported conflict strategy: {conflict_strategy}")
        backup_in_use = backup_path or _derive_backup_path(new_target)
        actions.append(f"Backup: {new_target} -> {backup_in_use}")

    actions.append(f"Move: {current_target} -> {new_target}")
    if materialize_links:
        for link in links_list:
            actions.append(f"Inline: {link} <= {new_target}")
    else:
        suffix = " (relative)" if use_relative_links else " (absolute)"
        for link in links_list:
            actions.append(f"Link: {link} -> {new_target}{suffix}")

    if dry_run:
        return actions

    if backup_in_use:
        if backup_in_use.exists():
            raise MigrationError(f"Backup destination exists: {backup_in_use}")
        try:
            new_target.rename(backup_in_use)
        except OSError as exc:
            raise MigrationError(f"Failed to backup existing destination: {exc}") from exc

    _safe_move_dir(current_target, new_target)
    if materialize_links:
        for link in links_list:
            if link.is_symlink():
                link.unlink()
            elif link.exists() and not link.is_dir():
                raise MigrationError(f"Cannot inline over existing non-dir: {link}")
            # When new_target shares the same path as one of the links, the move
            # above already materialised it; skip copying in that case.
            if link == new_target:
                continue
            shutil.copytree(new_target, link)
    else:
        for link in links_list:
            _retarget_symlink(link, new_target, make_relative=use_relative_links)

    if not new_target.exists():
        raise MigrationError(f"Move failed, missing: {new_target}")
    if materialize_links:
        for link in links_list:
            if not link.exists():
                raise MigrationError(f"Materialized path missing: {link}")
            if link.is_symlink():
                raise MigrationError(f"Materialized path still a symlink: {link}")
            if not link.is_dir():
                raise MigrationError(f"Materialized path is not a directory: {link}")
    else:
        for link in links_list:
            if Path(link).resolve(strict=True) != new_target:
                raise MigrationError(f"Verification failed for symlink: {link}")
    return actions


def rewrite_links_to_relative(
    infos: Iterable[SymlinkInfo], *, dry_run: bool = True
) -> List[str]:
    """Rewrite discovered symlinks to relative targets without moving data."""

    infos_list = list(infos)
    actions: List[str] = []

    def _compute_relative(link: Path, target: Path) -> str:
        try:
            return os.path.relpath(target, start=link.parent)
        except Exception as exc:
            raise MigrationError(f"无法计算相对路径: {link} -> {target}: {exc}") from exc

    for info in infos_list:
        rel = _compute_relative(info.source, info.target)
        actions.append(f"Retarget: {info.source} -> {rel} (target={info.target})")

    if dry_run:
        return actions

    for info in infos_list:
        _retarget_symlink(info.source, info.target, make_relative=True)

    for info in infos_list:
        if Path(info.source).resolve(strict=True) != info.target.resolve():
            raise MigrationError(f"Verification failed for symlink: {info.source}")
        raw = os.readlink(info.source)
        if os.path.isabs(raw):
            raise MigrationError(f"Link is still absolute: {info.source}")

    return actions


__all__ = [
    "MigrationError",
    "_safe_move_dir",
    "_derive_backup_path",
    "migrate_target_and_update_links",
    "rewrite_links_to_relative",
]
