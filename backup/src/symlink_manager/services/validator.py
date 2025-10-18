from __future__ import annotations

"""Validation utilities for proposed target changes (Task-5).

The validator performs conservative checks to prevent dangerous operations:
- Absolute path requirement
- Parent directory existence and writability
- No-op changes (same as current target)
- Avoid common system directories
- Optional scan-root guidance (warn when outside)

It intentionally errs on the side of safety. Migration logic remains
responsible for backups and atomic operations (Task-6).
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple
import os

from ..core.scanner import SymlinkInfo


FORBIDDEN_PREFIXES: tuple[str, ...] = (
    "/usr",
    "/System",
    "/etc",
    "/bin",
    "/sbin",
    "/var",
)


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    errors: List[str]
    warnings: List[str]


def _is_writable_directory(path: Path) -> bool:
    try:
        return path.is_dir() and os.access(path, os.W_OK | os.X_OK)
    except Exception:
        return False


def validate_target_change(
    symlink: SymlinkInfo,
    new_target: Path,
    *,
    scan_root: Optional[Path] = None,
) -> ValidationResult:
    """Validate a proposed new target location for a symlink's referenced object.

    The intent is to validate the destination where the real file/dir would be
    migrated to (Task-6), not the symlink path itself.
    """
    errors: List[str] = []
    warnings: List[str] = []

    # Basic sanity
    if not isinstance(new_target, Path):
        errors.append("New target must be a filesystem path.")
        return ValidationResult(False, errors, warnings)

    if not new_target.is_absolute():
        errors.append("Please provide an absolute path (e.g., /Users/you/... ).")
        return ValidationResult(False, errors, warnings)

    # Forbid obviously dangerous destinations
    for prefix in FORBIDDEN_PREFIXES:
        try:
            if str(new_target).startswith(prefix + "/") or str(new_target) == prefix:
                errors.append(f"Destination under forbidden system path: {prefix}")
                break
        except Exception:
            # Defensive; string ops should not fail
            pass

    # No-op change
    try:
        current = symlink.target
        # Compare realpaths without requiring existence for current target
        if current.resolve(strict=False) == new_target.resolve(strict=False):
            errors.append("New target is identical to current target (no change).")
    except Exception:
        # If resolution fails, fall back to raw string comparison
        if str(current) == str(new_target):
            errors.append("New target is identical to current target (no change).")

    # Parent directory must exist and be writable to perform migration
    parent = new_target.parent
    if not parent.exists():
        errors.append(f"Parent directory does not exist: {parent}")
    elif not _is_writable_directory(parent):
        errors.append(f"Insufficient permissions to write into: {parent}")

    # If destination exists and is not the same inode as current, be conservative
    if new_target.exists():
        try:
            same = False
            if symlink.target.exists():
                same = os.stat(new_target).st_ino == os.stat(symlink.target).st_ino and (
                    os.stat(new_target).st_dev == os.stat(symlink.target).st_dev
                )
            if not same:
                errors.append(
                    "Destination already exists and is different from current target;"
                    " refusing to overwrite. Choose a new path."
                )
        except Exception:
            errors.append(
                "Could not safely compare destination and current target; choose a different path."
            )

    # Guidance when outside the typical working area
    if scan_root is not None:
        try:
            new_target.relative_to(scan_root)
        except Exception:
            warnings.append(
                f"Destination is outside the scan root ({scan_root}); ensure this is intended."
            )

    # Check ability to later update the symlink itself (directory must be writable)
    link_parent = symlink.path.parent
    if not _is_writable_directory(link_parent):
        warnings.append(
            f"Symlink location's directory is not writable: {link_parent}."
            " Migration may fail when updating the link."
        )

    ok = len(errors) == 0
    return ValidationResult(ok, errors, warnings)

