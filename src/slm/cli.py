import argparse
import os
import shutil
import sys
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple, Any
from contextlib import suppress

try:
    import questionary
except Exception:  # pragma: no cover
    questionary = None

from .config import (
    ConfigError,
    LoadedConfig,
    coerce_scan_roots,
    load_config,
)


# -------------------------
# Scanning utilities
# -------------------------

@dataclass(frozen=True)
class SymlinkInfo:
    source: Path  # the symlink path
    target: Path  # resolved absolute target path


def _is_symlink_dir(p: Path) -> bool:
    try:
        return p.is_symlink() and p.resolve(strict=True).is_dir()
    except FileNotFoundError:
        return False


def _resolve_symlink_target_abs(p: Path) -> Path:
    # Do not use readlink directly; resolve handles relative targets
    return p.resolve(strict=True)


def scan_symlinks_pointing_into_data(
    scan_roots: Iterable[Path], data_root: Path, excludes: Tuple[str, ...] = (".git", "Library", ".cache", "node_modules", ".venv", "venv")
) -> List[SymlinkInfo]:
    data_root = data_root.resolve()
    found: List[SymlinkInfo] = []
    for root in scan_roots:
        root = root.expanduser().resolve()
        for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
            # prune excludes
            dirnames[:] = [d for d in dirnames if d not in excludes]
            # check directory entries that are symlinks
            for name in list(dirnames) + filenames:
                p = Path(dirpath) / name
                if not p.is_symlink():
                    continue
                try:
                    target = _resolve_symlink_target_abs(p)
                except FileNotFoundError:
                    continue  # broken symlink
                if not target.is_dir():
                    continue
                try:
                    target.relative_to(data_root)
                except ValueError:
                    continue  # not inside data_root
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
        """Sort targets by path relative to data_root when possible.

        Falls back to absolute path if the target is not within data_root.
        """
        try:
            rel = p.resolve().relative_to(data_root)
            return str(rel).lower()
        except Exception:
            return str(p.resolve()).lower()

    # Stable order by relative path for nicer UX in menus
    return dict(sorted(grouped.items(), key=lambda kv: _sort_key(kv[0])))


# -------------------------
# Migration (minimal, safe-first)
# -------------------------

class MigrationError(RuntimeError):
    pass


def _safe_move_dir(old: Path, new: Path) -> None:
    if new.exists():
        raise MigrationError(f"Destination exists: {new}")
    try:
        old.rename(new)
    except OSError as e:
        # cross-device move fallback
        if getattr(e, "errno", None) == 18 or "cross-device" in str(e).lower():
            shutil.copytree(old, new)
            shutil.rmtree(old)
        else:
            raise


def _derive_backup_path(target: Path, now: Optional[float] = None) -> Path:
    """Return a timestamp-based backup path for an existing target.

    Example: /path/to/dir -> /path/to/dir~20251018-132455
    """
    timestamp = time.strftime("%Y%m%d-%H%M%S", time.localtime(now or time.time()))
    base = target.with_name(f"{target.name}~{timestamp}")
    candidate = base
    counter = 1
    while candidate.exists():
        candidate = target.with_name(f"{target.name}~{timestamp}-{counter}")
        counter += 1
    return candidate


def _retarget_symlink(link: Path, new_target: Path) -> None:
    if not link.is_symlink():
        raise MigrationError(f"Not a symlink: {link}")
    link.unlink()
    os.symlink(str(new_target), str(link))


def migrate_target_and_update_links(
    current_target: Path,
    new_target: Path,
    links: Iterable[Path],
    dry_run: bool = True,
    conflict_strategy: str = "abort",
    backup_path: Optional[Path] = None,
) -> List[str]:
    actions: List[str] = []
    current_target = current_target.resolve()
    new_target = new_target.expanduser().resolve()

    if current_target == new_target:
        raise MigrationError("New target equals current target.")
    try:
        current_target.relative_to("/")
        new_target.relative_to("/")
    except Exception:
        pass  # paths are absolute already by resolve
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
    for link in links:
        actions.append(f"Link: {link} -> {new_target}")

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
    for link in links:
        _retarget_symlink(link, new_target)

    # verify
    if not new_target.exists():
        raise MigrationError(f"Move failed, missing: {new_target}")
    for link in links:
        if Path(link).resolve(strict=True) != new_target:
            raise MigrationError(f"Verification failed for symlink: {link}")
    return actions


# -------------------------
# CLI
# -------------------------
def _fast_tree_summary(path: Path) -> Tuple[int, int]:
    """Return (file_count, total_bytes) for a directory tree quickly.

    - Counts only regular files; ignores symlinks and special files.
    - Does not follow symlinks.
    - Skips entries on PermissionError/ENOENT without failing.
    """
    path = Path(path)
    if not path.exists() or not path.is_dir():
        return (0, 0)

    files = 0
    total_bytes = 0
    stack: List[Path] = [path]
    while stack:
        d = stack.pop()
        try:
            with os.scandir(d) as it:
                for entry in it:
                    # Skip broken entries permissively
                    with suppress(FileNotFoundError, PermissionError, OSError):
                        if entry.is_dir(follow_symlinks=False):
                            stack.append(Path(entry.path))
                            continue
                        if entry.is_file(follow_symlinks=False):
                            files += 1
                            with suppress(FileNotFoundError, PermissionError, OSError):
                                st = entry.stat(follow_symlinks=False)
                                total_bytes += int(getattr(st, "st_size", 0))
        except (FileNotFoundError, PermissionError, NotADirectoryError, OSError):
            # Directory vanished or not accessible; skip
            continue
    return (files, total_bytes)

def _fmt_summary_pair(curr: Tuple[int, int], new: Tuple[int, int]) -> str:
    return (
        f"summary(current=files:{curr[0]} bytes:{curr[1]}, "
        f"new=files:{new[0]} bytes:{new[1]})"
    )

def _parse_args(argv):
    p = argparse.ArgumentParser(
        prog="slm",
        description="符号链接目标迁移（Questionary 交互界面）",
    )
    p.add_argument(
        "--data-root",
        default=None,
        help="Data directory containing real folders (default: ~/Developer/Data)",
    )
    p.add_argument(
        "--scan-roots",
        nargs="*",
        default=None,
        help="Roots to scan for symlink sources (default: ~)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Preview actions without making changes",
    )
    p.add_argument(
        "--log-json",
        dest="log_json",
        default=None,
        help="Append JSON Lines records of planned/applied actions to the given file",
    )
    return p.parse_args(argv)


def _append_json_log(
    path: Path,
    phase: str,
    current_target: Path,
    new_target: Path,
    links: Iterable[Path],
    backup_entry: Optional[Tuple[Path, Path]] = None,
) -> None:
    """Append action records as JSON Lines.

    Each line is an object with keys: phase, type, from/to or link/to, ts.
    """
    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    ts = time.time()
    records = []
    if backup_entry:
        records.append(
            {
                "phase": phase,
                "type": "backup",
                "from": str(backup_entry[0]),
                "to": str(backup_entry[1]),
                "ts": ts,
            }
        )
    records.append(
        {
            "phase": phase,
            "type": "move",
            "from": str(current_target),
            "to": str(new_target),
            "ts": ts,
        }
    )
    for link in links:
        records.append(
            {
                "phase": phase,
                "type": "retarget",
                "link": str(link),
                "to": str(new_target),
                "ts": ts,
            }
        )
    with path.open("a", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def main(argv=None):
    default_data_root = Path.home() / "Developer" / "Data"
    default_scan_roots = [str(Path.home())]
    argv = sys.argv[1:] if argv is None else argv
    args = _parse_args(argv)

    if questionary is None:
        print("未安装 questionary，请先安装依赖。")
        return 2

    try:
        loaded_config: LoadedConfig = load_config()
    except ConfigError as exc:
        print(f"配置错误：{exc}")
        return 2

    config_data: Dict[str, Any] = loaded_config.data

    if args.data_root is not None:
        data_root_str = args.data_root
    else:
        data_root_str = config_data.get("data_root", None)
    if data_root_str is None:
        data_root_str = str(default_data_root)
    if not isinstance(data_root_str, str):
        print("配置错误：data_root 必须是字符串。")
        return 2
    data_root = Path(data_root_str).expanduser().resolve()

    if args.scan_roots is not None:
        scan_roots_raw = args.scan_roots
    else:
        try:
            scan_roots_raw = coerce_scan_roots(
                config_data.get("scan_roots"),
                context=str(loaded_config.path) if loaded_config.path else "配置文件",
            )
        except ConfigError as exc:
            print(f"配置错误：{exc}")
            return 2
        if not scan_roots_raw:
            scan_roots_raw = default_scan_roots

    scan_roots = [Path(p).expanduser() for p in scan_roots_raw]

    if loaded_config.path:
        print(f"已加载配置文件：{loaded_config.path}")

    print(f"SLM 已准备。Data 根：{data_root} | Dry-run：{args.dry_run}")

    infos = scan_symlinks_pointing_into_data(scan_roots, data_root)
    grouped = group_by_target_within_data(infos, data_root)

    if not grouped:
        print("未找到指向 Data 目录的符号链接。请检查扫描范围或目录。")
        return 0

    def _fmt_target(t: Path, count: int) -> str:
        try:
            rel = t.relative_to(data_root)
        except ValueError:
            rel = t
        return f"{rel}  ({count} 个链接)"

    choices = [
        questionary.Choice(title=_fmt_target(t, len(links)), value=t)
        for t, links in grouped.items()
    ]
    choices.append(questionary.Choice(title="退出", value=None))

    selected_target = questionary.select(
        "选择一个被指向的目标文件夹:", choices=choices
    ).ask()

    if not selected_target:
        return 0

    links = [info.source for info in grouped[selected_target]]
    display_links = "\n".join(f"- {p}" for p in links)
    print(f"以下符号链接指向该目录:\n{display_links}")

    default_new = str(selected_target)
    new_path_str = questionary.text(
        "输入新的目标绝对路径:", default=default_new
    ).ask()
    if not new_path_str:
        print("未输入新路径，已取消。")
        return 0

    new_target = Path(new_path_str).expanduser()

    conflict_strategy = "abort"
    backup_path: Optional[Path] = None
    if new_target.exists():
        print(f"目标路径已存在：{new_target}")
        backup_candidate = _derive_backup_path(new_target)
        strategy_choice = questionary.select(
            "选择冲突处理策略：",
            choices=[
                questionary.Choice(title="中止（默认，保持现状）", value="abort"),
                questionary.Choice(
                    title=f"备份后迁移（先重命名为 {backup_candidate.name}）", value="backup"
                ),
                questionary.Choice(title="强制覆盖（不支持）", value="reject"),
            ],
            default="abort",
        ).ask()
        if strategy_choice == "reject":
            print("强制覆盖暂不支持，已中止。")
            return 0
        if strategy_choice == "abort" or strategy_choice is None:
            print("已中止迁移。")
            return 0
        conflict_strategy = "backup"
        backup_path = backup_candidate

    try:
        plan = migrate_target_and_update_links(
            selected_target,
            new_target,
            links,
            dry_run=args.dry_run,
            conflict_strategy=conflict_strategy,
            backup_path=backup_path,
        )
    except MigrationError as e:
        print(f"校验失败：{e}")
        return 2

    if args.dry_run:
        print("计划 (dry-run):")
        for line in plan:
            print(f"  • {line}")
        # Fast tree summaries for preview
        curr_summary = _fast_tree_summary(selected_target)
        new_summary = _fast_tree_summary(new_target) if new_target.exists() else (0, 0)
        print(_fmt_summary_pair(curr_summary, new_summary))
        if args.log_json:
            _append_json_log(
                args.log_json,
                "preview",
                selected_target,
                new_target,
                links,
                backup_entry=(new_target, backup_path) if backup_path else None,
            )
        proceed = questionary.confirm("执行上述操作吗？", default=False).ask()
        if not proceed:
            print("已取消。")
            return 0
        # execute for real after confirmation
        try:
            migrate_target_and_update_links(
                selected_target,
                new_target,
                links,
                dry_run=False,
                conflict_strategy=conflict_strategy,
                backup_path=backup_path,
            )
        except MigrationError as e:
            print(f"执行失败：{e}")
            return 2
        if args.log_json:
            _append_json_log(
                args.log_json,
                "applied",
                selected_target,
                new_target,
                links,
                backup_entry=(new_target, backup_path) if backup_path else None,
            )
        # Final summary for new target after apply
        final_new = _fast_tree_summary(new_target)
        print(f"summary(new=files:{final_new[0]} bytes:{final_new[1]})")
    else:
        # Non-dry-run invocation: operation already applied above
        final_new = _fast_tree_summary(new_target)
        print(f"summary(new=files:{final_new[0]} bytes:{final_new[1]})")

    print("完成。已验证符号链接指向新目标。")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
