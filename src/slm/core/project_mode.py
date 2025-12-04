"""Project-level data directory status API.

This module provides functions for querying and modifying the data
directory link mode of a specific project, designed for integration
with repo-sign and other project management tools.

Usage:
    from slm.core.project_mode import (
        ProjectDataStatus,
        LinkMode,
        get_project_data_status,
        set_project_data_mode,
    )

    # Query project data status
    status = get_project_data_status(
        project_root=Path("/path/to/project"),
        data_root=Path("~/Developer/Data"),
    )
    print(f"Mode: {status.mode}, Target: {status.target_path}")

    # Change link mode
    new_status = set_project_data_mode(
        project_root=Path("/path/to/project"),
        data_root=Path("~/Developer/Data"),
        mode="relative",
    )
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Literal, Optional

from .migration import (
    MigrationError,
    _retarget_symlink,
    _materialize_link,
)

# Type alias for link modes
LinkMode = Literal["relative", "absolute", "inline", "missing"]

# Fixed data directory name (per [#Q15] decision)
DATA_DIR_NAME = "data"


@dataclass
class ProjectDataStatus:
    """Status of a project's data directory.

    Attributes:
        project_root: The project's root directory.
        data_path: Path to the data directory (project_root / "data"), or None if missing.
        mode: Current link mode - relative, absolute, inline, or missing.
        link_text: Raw symlink target string from os.readlink(), or None.
        target_path: Resolved absolute path to the actual data directory, or None.
        shared_with: List of other project roots that share the same target.
    """

    project_root: Path
    data_path: Optional[Path]
    mode: LinkMode
    link_text: Optional[str]
    target_path: Optional[Path]
    shared_with: List[Path] = field(default_factory=list)


def get_project_data_status(
    project_root: Path,
    data_root: Path,
    all_project_roots: Optional[List[Path]] = None,
) -> ProjectDataStatus:
    """Get the data directory status for a project.

    Args:
        project_root: The project's root directory.
        data_root: The root directory where data folders are stored.
        all_project_roots: Optional list of all project roots for shared_with calculation.

    Returns:
        ProjectDataStatus with mode, paths, and sharing information.

    Examples:
        >>> status = get_project_data_status(Path("/my/project"), Path("~/Developer/Data"))
        >>> print(status.mode)  # 'relative', 'absolute', 'inline', or 'missing'
    """
    project_root = Path(project_root).expanduser().resolve()
    data_root = Path(data_root).expanduser().resolve()
    data_path = project_root / DATA_DIR_NAME

    # Case 1: Data directory doesn't exist
    if not data_path.exists() and not data_path.is_symlink():
        return ProjectDataStatus(
            project_root=project_root,
            data_path=data_path,
            mode="missing",
            link_text=None,
            target_path=None,
            shared_with=[],
        )

    # Case 2: Broken symlink
    if data_path.is_symlink():
        try:
            target = data_path.resolve(strict=True)
        except (FileNotFoundError, OSError):
            return ProjectDataStatus(
                project_root=project_root,
                data_path=data_path,
                mode="missing",
                link_text=os.readlink(str(data_path)),
                target_path=None,
                shared_with=[],
            )

        # Case 3: Valid symlink
        link_text = os.readlink(str(data_path))
        is_absolute = os.path.isabs(link_text)
        mode: LinkMode = "absolute" if is_absolute else "relative"

        shared_with = _find_shared_projects(
            target, project_root, all_project_roots
        ) if all_project_roots else []

        return ProjectDataStatus(
            project_root=project_root,
            data_path=data_path,
            mode=mode,
            link_text=link_text,
            target_path=target,
            shared_with=shared_with,
        )

    # Case 4: Real directory (inline)
    return ProjectDataStatus(
        project_root=project_root,
        data_path=data_path,
        mode="inline",
        link_text=None,
        target_path=data_path,
        shared_with=[],
    )


def _find_shared_projects(
    target_path: Path,
    current_project: Path,
    all_project_roots: List[Path],
) -> List[Path]:
    """Find other projects that share the same data target.

    Args:
        target_path: The resolved target path to match against.
        current_project: The current project (excluded from results).
        all_project_roots: List of all project roots to check.

    Returns:
        List of project roots that share the same target.
    """
    shared = []
    target_path = target_path.resolve()

    for project in all_project_roots:
        project = Path(project).expanduser().resolve()

        # Skip self
        if project == current_project:
            continue

        data_path = project / DATA_DIR_NAME

        # Check if it's a symlink pointing to the same target
        if data_path.is_symlink():
            try:
                other_target = data_path.resolve(strict=True)
                if other_target == target_path:
                    shared.append(project)
            except (FileNotFoundError, OSError):
                continue

    return shared


def set_project_data_mode(
    project_root: Path,
    data_root: Path,
    mode: LinkMode,
    dry_run: bool = False,
) -> ProjectDataStatus:
    """Set the data directory link mode for a project.

    Args:
        project_root: The project's root directory.
        data_root: The root directory where data folders are stored.
        mode: Target mode - 'relative', 'absolute', or 'inline'.
        dry_run: If True, only return what would happen without making changes.

    Returns:
        ProjectDataStatus reflecting the new state (or projected state if dry_run).

    Raises:
        MigrationError: If the data directory is missing or operation fails.

    Examples:
        >>> set_project_data_mode(Path("/my/project"), Path("~/Developer/Data"), "relative")
    """
    if mode == "missing":
        raise MigrationError("Cannot set mode to 'missing'")

    project_root = Path(project_root).expanduser().resolve()
    data_root = Path(data_root).expanduser().resolve()
    data_path = project_root / DATA_DIR_NAME

    # Get current status
    current_status = get_project_data_status(project_root, data_root)

    if current_status.mode == "missing":
        raise MigrationError(
            f"Cannot set mode: data directory does not exist at {data_path}"
        )

    # Already in target mode
    if current_status.mode == mode:
        return current_status

    if dry_run:
        # Return projected status
        return ProjectDataStatus(
            project_root=project_root,
            data_path=data_path,
            mode=mode,
            link_text=current_status.link_text,
            target_path=current_status.target_path,
            shared_with=current_status.shared_with,
        )

    # Perform mode change
    if mode == "inline":
        # Convert symlink to real directory
        if current_status.mode in ("relative", "absolute"):
            _materialize_link(current_status.target_path, data_path)
    elif mode in ("relative", "absolute"):
        if current_status.mode == "inline":
            # Cannot convert inline to symlink without specifying target
            raise MigrationError(
                "Cannot convert inline directory to symlink without target. "
                "Use the interactive CLI or migration functions directly."
            )
        else:
            # Convert between relative and absolute
            _retarget_symlink(
                data_path,
                current_status.target_path,
                make_relative=(mode == "relative"),
            )

    # Return new status
    return get_project_data_status(project_root, data_root)


__all__ = [
    "LinkMode",
    "ProjectDataStatus",
    "DATA_DIR_NAME",
    "get_project_data_status",
    "set_project_data_mode",
]
