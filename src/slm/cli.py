import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

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
from .core import (
    MigrationError,
    _derive_backup_path,
    _safe_move_dir,
    fast_tree_summary,
    format_summary_pair,
    group_by_target_within_data,
    move_and_delete_links,
    materialize_links_in_place,
    migrate_target_and_update_links,
    rewrite_links_to_relative,
    SymlinkInfo,
    scan_symlinks_pointing_into_data,
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
        help="Roots to scan for symlink sources (default: ~/Developer/Cloud/Dropbox/-Code-/Scripts)",
    )
    p.add_argument(
        "--link-mode",
        choices=["relative", "absolute", "inline"],
        default=None,
        help="How to handle links: relative/absolute symlinks or inline copies; omit to choose interactively",
    )
    p.add_argument(
        "--relative",
        action="store_true",
        help="Rewrite found symlinks to relative paths without moving their targets",
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
    link_mode: str = "relative",
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
            "link_mode": link_mode,
            "ts": ts,
        }
    )
    record_type = "materialize" if link_mode == "inline" else "retarget"
    for link in links:
        records.append(
            {
                "phase": phase,
                "type": record_type,
                "link": str(link),
                "to": str(new_target),
                "link_mode": link_mode,
                "ts": ts,
            }
        )
    with path.open("a", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _append_move_only_log(
    path: Path,
    phase: str,
    current_target: Path,
    new_target: Path,
    links: Iterable[Path],
    backup_entry: Optional[Tuple[Path, Path]] = None,
) -> None:
    """Append move-only action records (move + unlink) as JSON Lines."""

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
            "link_mode": "move-only",
            "ts": ts,
        }
    )
    for link in links:
        records.append(
            {
                "phase": phase,
                "type": "unlink",
                "link": str(link),
                "ts": ts,
            }
        )
    with path.open("a", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _append_relative_only_log(
    path: Path, phase: str, infos: Iterable[SymlinkInfo]
) -> None:
    """Append retarget-only action records as JSON Lines."""

    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    ts = time.time()
    records = []
    for info in infos:
        records.append(
            {
                "phase": phase,
                "type": "retarget",
                "link": str(info.source),
                "to": str(info.target),
                "link_mode": "relative-only",
                "ts": ts,
            }
        )
    with path.open("a", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _append_materialize_log(
    path: Path, phase: str, source_target: Path, links: Iterable[Path]
) -> None:
    """Append materialize action records as JSON Lines.

    Records inline mode operations where source data is copied to link locations
    without moving the original data.
    """
    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    ts = time.time()
    records = []
    for link in links:
        records.append(
            {
                "phase": phase,
                "type": "materialize",
                "link": str(link),
                "source": str(source_target),
                "link_mode": "inline",
                "ts": ts,
            }
        )
    with path.open("a", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def main(argv=None):
    default_data_root = Path.home() / "Developer" / "Data"
    default_scan_roots = [
        str(Path.home() / "Developer" / "Cloud" / "Dropbox" / "-Code-" / "Scripts")
    ]
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

    link_mode_label = args.link_mode or "interactive"
    print(
        f"SLM 已准备。Data 根：{data_root} | Dry-run：{args.dry_run} | 链接模式：{link_mode_label}"
    )

    infos = scan_symlinks_pointing_into_data(scan_roots, data_root)

    if args.relative:
        if not infos:
            print("未找到指向 Data 目录的符号链接。请检查扫描范围或目录。")
            return 0
        plan = rewrite_links_to_relative(infos, dry_run=args.dry_run)
        print("计划 (relative-only):")
        for line in plan:
            print(f"  • {line}")
        if args.log_json:
            _append_relative_only_log(args.log_json, "preview", infos)
        if args.dry_run:
            proceed = questionary.confirm(
                "执行上述操作（仅改写为相对路径）吗？", default=False
            ).ask()
            if not proceed:
                print("已取消。")
                return 0
        try:
            rewrite_links_to_relative(infos, dry_run=False)
        except MigrationError as exc:
            print(f"执行失败：{exc}")
            return 2
        if args.log_json:
            _append_relative_only_log(args.log_json, "applied", infos)
        print("完成。已将符号链接改写为相对路径（未移动目录）。")
        return 0

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

    # Graceful exit handling across Questionary versions:
    # - Expected: our "退出" choice returns value=None
    # - Some environments may return the label string (e.g., "退出")
    # - Also handle unexpected values not present in grouped keys
    if selected_target is None or selected_target not in grouped:
        print("已取消。")
        return 0

    links = [info.source for info in grouped[selected_target]]
    display_links = "\n".join(f"- {p}" for p in links)
    print(f"以下符号链接指向该目录:\n{display_links}")

    operation_kind = None
    if args.link_mode is None:
        operation_choice = questionary.select(
            "选择操作类型：",
            choices=[
                questionary.Choice(
                    title="本地化（Materialize）：复制数据到链接位置，保留原数据",
                    value="materialize",
                ),
                questionary.Choice(
                    title="迁移 + 相对路径链接：移动数据并创建相对符号链接",
                    value="relative",
                ),
                questionary.Choice(
                    title="迁移 + 绝对路径链接：移动数据并创建绝对符号链接",
                    value="absolute",
                ),
                questionary.Choice(
                    title="仅移动（Move Only）：移动数据并删除所有符号链接",
                    value="move-only",
                ),
                questionary.Choice(title="退出", value="exit"),
            ],
        ).ask()
        if operation_choice in (None, "exit"):
            print("已取消。")
            return 0
        operation_kind = operation_choice
    else:
        operation_kind = "materialize" if args.link_mode == "inline" else args.link_mode

    # Materialize: copy data to link locations, preserve original
    if operation_kind == "materialize":
        curr_summary = fast_tree_summary(selected_target)
        plan = materialize_links_in_place(selected_target, links, dry_run=True)
        print("计划 (inline/materialize):")
        for line in plan:
            print(f"  • {line}")
        print(f"源目录摘要：files={curr_summary[0]} bytes={curr_summary[1]}")
        print("注意：原数据目录将保留，数据将被复制到各链接位置。")
        if args.log_json:
            _append_materialize_log(args.log_json, "preview", selected_target, links)
        proceed = questionary.confirm("执行上述操作吗？", default=False).ask()
        if not proceed:
            print("已取消。")
            return 0
        try:
            materialize_links_in_place(selected_target, links, dry_run=False)
        except MigrationError as e:
            print(f"执行失败：{e}")
            return 2
        if args.log_json:
            _append_materialize_log(args.log_json, "applied", selected_target, links)
        print("完成。已将符号链接替换为数据副本（原数据保留）。")
        return 0

    # Operations requiring a new target path
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
        if operation_kind == "move-only":
            plan = move_and_delete_links(
                selected_target,
                new_target,
                links,
                dry_run=args.dry_run,
                conflict_strategy=conflict_strategy,
                backup_path=backup_path,
                data_root=data_root,
            )
        else:
            plan = migrate_target_and_update_links(
                selected_target,
                new_target,
                links,
                dry_run=args.dry_run,
                conflict_strategy=conflict_strategy,
                backup_path=backup_path,
                data_root=data_root,
                link_mode=operation_kind,
            )
    except MigrationError as e:
        print(f"校验失败：{e}")
        return 2

    if args.dry_run:
        print("计划 (dry-run):")
        for line in plan:
            print(f"  • {line}")
        # Fast tree summaries for preview
        curr_summary = fast_tree_summary(selected_target)
        new_summary = fast_tree_summary(new_target) if new_target.exists() else (0, 0)
        print(format_summary_pair(curr_summary, new_summary))
        if args.log_json:
            if operation_kind == "move-only":
                _append_move_only_log(
                    args.log_json,
                    "preview",
                    selected_target,
                    new_target,
                    links,
                    backup_entry=(new_target, backup_path) if backup_path else None,
                )
            else:
                _append_json_log(
                    args.log_json,
                    "preview",
                    selected_target,
                    new_target,
                    links,
                    backup_entry=(new_target, backup_path) if backup_path else None,
                    link_mode=operation_kind,
                )
        proceed = questionary.confirm("执行上述操作吗？", default=False).ask()
        if not proceed:
            print("已取消。")
            return 0
        # execute for real after confirmation
        try:
            if operation_kind == "move-only":
                move_and_delete_links(
                    selected_target,
                    new_target,
                    links,
                    dry_run=False,
                    conflict_strategy=conflict_strategy,
                    backup_path=backup_path,
                    data_root=data_root,
                )
            else:
                migrate_target_and_update_links(
                    selected_target,
                    new_target,
                    links,
                    dry_run=False,
                    conflict_strategy=conflict_strategy,
                    backup_path=backup_path,
                    data_root=data_root,
                    link_mode=operation_kind,
                )
        except MigrationError as e:
            print(f"执行失败：{e}")
            return 2
        if args.log_json:
            if operation_kind == "move-only":
                _append_move_only_log(
                    args.log_json,
                    "applied",
                    selected_target,
                    new_target,
                    links,
                    backup_entry=(new_target, backup_path) if backup_path else None,
                )
            else:
                _append_json_log(
                    args.log_json,
                    "applied",
                    selected_target,
                    new_target,
                    links,
                    backup_entry=(new_target, backup_path) if backup_path else None,
                    link_mode=operation_kind,
                )
        # Final summary for new target after apply
        final_new = fast_tree_summary(new_target)
        print(f"summary(new=files:{final_new[0]} bytes:{final_new[1]})")
    else:
        # Non-dry-run invocation: operation already applied above
        final_new = fast_tree_summary(new_target)
        print(f"summary(new=files:{final_new[0]} bytes:{final_new[1]})")

    if operation_kind == "move-only":
        print("完成。已移动目录并删除关联符号链接。")
    else:
        print("完成。已验证符号链接指向新目标。")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
