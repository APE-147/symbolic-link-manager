"""Scanning helpers for discovering qualified symlink targets."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


@dataclass(frozen=True)
class SymlinkInfo:
    """Represents a directory symlink and its resolved absolute target."""

    source: Path
    target: Path


def _is_symlink_dir(p: Path) -> bool:
    try:
        return p.is_symlink() and p.resolve(strict=True).is_dir()
    except FileNotFoundError:
        return False


def _resolve_symlink_target_abs(p: Path) -> Path:
    """Resolve the symlink target, handling relative paths safely."""

    return p.resolve(strict=True)


def scan_symlinks_pointing_into_data(
    scan_roots: Iterable[Path],
    data_root: Path,
    excludes: Tuple[str, ...] = (
        ".git",
        "Library",
        ".cache",
        "node_modules",
        ".venv",
        "venv",
    ),
) -> List[SymlinkInfo]:
    data_root = data_root.resolve()
    found: List[SymlinkInfo] = []
    for root in scan_roots:
        root = root.expanduser().resolve()
        for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
            dirnames[:] = [d for d in dirnames if d not in excludes]
            for name in list(dirnames) + filenames:
                p = Path(dirpath) / name
                if not p.is_symlink():
                    continue
                try:
                    target = _resolve_symlink_target_abs(p)
                except FileNotFoundError:
                    continue
                if not target.is_dir():
                    continue
                try:
                    target.relative_to(data_root)
                except ValueError:
                    continue
                found.append(SymlinkInfo(source=p, target=target))
    return found


def group_by_target_within_data(
    infos: Iterable[SymlinkInfo], data_root: Path
) -> Dict[Path, List[SymlinkInfo]]:
    grouped: Dict[Path, List[SymlinkInfo]] = {}
    for info in infos:
        key = info.target
        grouped.setdefault(key, []).append(info)

    data_root = Path(data_root).resolve()

    def _sort_key(p: Path) -> str:
        try:
            rel = p.resolve().relative_to(data_root)
            return str(rel).lower()
        except Exception:
            return str(p.resolve()).lower()

    return dict(sorted(grouped.items(), key=lambda kv: _sort_key(kv[0])))


__all__ = [
    "SymlinkInfo",
    "scan_symlinks_pointing_into_data",
    "group_by_target_within_data",
]
