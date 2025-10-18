import argparse
import json
import time
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple
from contextlib import suppress

try:
    import questionary
except Exception:  # pragma: no cover
    questionary = None


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
    # stable order by path relative to data_root
    return dict(
        sorted(grouped.items(), key=lambda kv: str(kv[0].resolve()).lower())
    )


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


def _retarget_symlink(link: Path, new_target: Path) -> None:
    if not link.is_symlink():
        raise MigrationError(f"Not a symlink: {link}")
    link.unlink()
    os.symlink(str(new_target), str(link))


def migrate_target_and_update_links(
    current_target: Path, new_target: Path, links: Iterable[Path], dry_run: bool = True
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

    actions.append(f"Move: {current_target} -> {new_target}")
    for link in links:
        actions.append(f"Link: {link} -> {new_target}")

    if dry_run:
        return actions

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
        description="Symlink target migration (Questionary UI)",
    )
    p.add_argument(
        "--data-root",
        default=str(Path.home() / "Developer" / "Data"),
        help="Data directory containing real folders (default: ~/Developer/Data)",
    )
    p.add_argument(
        "--scan-roots",
        nargs="*",
        default=[str(Path.home())],
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


def _append_json_log(path: Path, phase: str, current_target: Path, new_target: Path, links: Iterable[Path]) -> None:
    """Append action records as JSON Lines.

    Each line is an object with keys: phase, type, from/to or link/to, ts.
    """
    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    ts = time.time()
    records = []
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
    argv = sys.argv[1:] if argv is None else argv
    args = _parse_args(argv)

    if questionary is None:
        print("questionary is not installed. Please install dependencies.")
        return 2

    data_root = Path(args.data_root).expanduser().resolve()
    scan_roots = [Path(p) for p in (args.scan_roots or [])]
    print(f"SLM ready. Data root: {data_root} | Dry-run: {args.dry_run}")

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

    new_target = Path(new_path_str)

    try:
        plan = migrate_target_and_update_links(
            selected_target, new_target, links, dry_run=args.dry_run
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
            _append_json_log(args.log_json, "preview", selected_target, new_target, links)
        proceed = questionary.confirm("执行上述操作吗？", default=False).ask()
        if not proceed:
            print("已取消。")
            return 0
        # execute for real after confirmation
        try:
            migrate_target_and_update_links(
                selected_target, new_target, links, dry_run=False
            )
        except MigrationError as e:
            print(f"执行失败：{e}")
            return 2
        if args.log_json:
            _append_json_log(args.log_json, "applied", selected_target, new_target, links)
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
