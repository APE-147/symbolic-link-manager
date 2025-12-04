"""Core primitives for scanning, migrating, and summarising symlink targets."""

from .migration import (
    MigrationError,
    _derive_backup_path,
    _materialize_link,
    _safe_move_dir,
    move_and_delete_links,
    materialize_links_in_place,
    migrate_target_and_update_links,
    rewrite_links_to_relative,
)
from .scanner import (
    SymlinkInfo,
    group_by_target_within_data,
    scan_symlinks_pointing_into_data,
)
from .summary import fast_tree_summary, format_summary_pair
from .project_mode import (
    LinkMode,
    ProjectDataStatus,
    DATA_DIR_NAME,
    get_project_data_status,
    set_project_data_mode,
)

__all__ = [
    "MigrationError",
    "SymlinkInfo",
    "_derive_backup_path",
    "_materialize_link",
    "_safe_move_dir",
    "fast_tree_summary",
    "format_summary_pair",
    "group_by_target_within_data",
    "move_and_delete_links",
    "materialize_links_in_place",
    "migrate_target_and_update_links",
    "rewrite_links_to_relative",
    "scan_symlinks_pointing_into_data",
    "LinkMode",
    "ProjectDataStatus",
    "DATA_DIR_NAME",
    "get_project_data_status",
    "set_project_data_mode",
]
