from __future__ import annotations

from pathlib import Path
import os

import pytest

from symlink_manager.core.scanner import SymlinkInfo
from symlink_manager.services.validator import validate_target_change


def _mk_symlink(tmp_path: Path) -> SymlinkInfo:
    # Create a real file and a symlink to it
    target = tmp_path / "real.txt"
    target.write_text("hello")
    link = tmp_path / "link.txt"
    # Use relative link to exercise resolution code paths
    os.symlink("real.txt", link)
    return SymlinkInfo(path=link, name=link.name, target=target, is_broken=False, project=None)


def test_requires_absolute_path(tmp_path: Path):
    info = _mk_symlink(tmp_path)
    vr = validate_target_change(info, Path("relative/path.txt"), scan_root=tmp_path)
    assert not vr.ok
    assert any("absolute path" in e for e in vr.errors)


def test_parent_must_exist_and_writable(tmp_path: Path):
    info = _mk_symlink(tmp_path)
    missing_parent = tmp_path / "missing" / "dest.txt"
    vr_missing = validate_target_change(info, missing_parent, scan_root=tmp_path)
    assert not vr_missing.ok
    assert any("Parent directory does not exist" in e for e in vr_missing.errors)

    # Make a parent that exists but is not writable
    parent = tmp_path / "nowrite"
    parent.mkdir()
    try:
        parent.chmod(0o500)
        vr_nowrite = validate_target_change(info, parent / "dest.txt", scan_root=tmp_path)
        assert not vr_nowrite.ok
        assert any("Insufficient permissions" in e for e in vr_nowrite.errors)
    finally:
        # Restore perms for cleanup
        parent.chmod(0o700)


def test_noop_change_detected(tmp_path: Path):
    info = _mk_symlink(tmp_path)
    vr = validate_target_change(info, info.target, scan_root=tmp_path)
    assert not vr.ok
    assert any("identical to current target" in e for e in vr.errors)


def test_forbidden_system_prefixes_flagged(tmp_path: Path):
    info = _mk_symlink(tmp_path)
    vr = validate_target_change(info, Path("/usr/local/test.txt"), scan_root=tmp_path)
    assert not vr.ok
    assert any("forbidden system path" in e for e in vr.errors)


def test_warn_outside_scan_root(tmp_path: Path):
    info = _mk_symlink(tmp_path)
    outside = Path("/tmp") / "somewhere" / "dest.txt"
    # Ensure parent exists so we don't fail on missing parent (reduce flakiness)
    outside.parent.mkdir(parents=True, exist_ok=True)
    vr = validate_target_change(info, outside, scan_root=tmp_path)
    # May still fail on permissions, so assert only the warning presence if ok is False or True
    assert any("outside the scan root" in w for w in vr.warnings)


def test_existing_destination_conflict(tmp_path: Path):
    info = _mk_symlink(tmp_path)
    other = tmp_path / "other.txt"
    other.write_text("world")
    vr = validate_target_change(info, other, scan_root=tmp_path)
    assert not vr.ok
    assert any("Destination already exists" in e for e in vr.errors)

