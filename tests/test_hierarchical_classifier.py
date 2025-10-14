from __future__ import annotations

from pathlib import Path
from collections import OrderedDict
import os

import pytest

from symlink_manager.core.scanner import SymlinkInfo
from symlink_manager.core.classifier import (
    _extract_path_hierarchy,
    _detect_hierarchy_from_primary,
    classify_symlinks_auto_hierarchy,
)


def test_extract_path_hierarchy_basic(tmp_path: Path) -> None:
    """Test basic path hierarchy extraction from scan root."""
    scan_root = tmp_path / "Developer"
    scan_root.mkdir()

    # Test: scan_root/Desktop/Projects/MyApp/data
    symlink_path = scan_root / "Desktop" / "Projects" / "MyApp" / "data"
    secondary, project = _extract_path_hierarchy(symlink_path, scan_root)

    assert secondary == "Desktop"
    assert project == "Projects"


def test_extract_path_hierarchy_direct_under_scan_root(tmp_path: Path) -> None:
    """Test symlink directly under scan root."""
    scan_root = tmp_path
    symlink_path = scan_root / "mysymlink"

    secondary, project = _extract_path_hierarchy(symlink_path, scan_root)

    assert secondary == "root"
    assert project == "mysymlink"


def test_extract_path_hierarchy_two_levels(tmp_path: Path) -> None:
    """Test scan_root/folder/symlink structure."""
    scan_root = tmp_path
    symlink_path = scan_root / "Tools" / "mysymlink"

    secondary, project = _extract_path_hierarchy(symlink_path, scan_root)

    assert secondary == "Tools"
    assert project == "mysymlink"


def test_extract_path_hierarchy_not_relative_to_scan_root(tmp_path: Path) -> None:
    """Test fallback when path is not relative to scan root."""
    scan_root = tmp_path / "one"
    scan_root.mkdir()

    symlink_path = tmp_path / "different" / "path" / "to" / "symlink"

    secondary, project = _extract_path_hierarchy(symlink_path, scan_root)

    # Should fall back to using parent directories
    assert secondary == "to"
    assert project == "symlink"


def test_detect_hierarchy_from_primary_simple_pattern(tmp_path: Path) -> None:
    """Test hierarchy detection with simple wildcard pattern."""
    # Create a realistic structure that matches the pattern
    base = tmp_path / "Desktop"
    symlink_path = base / "Projects" / "MyApp" / "data"
    pattern = str(tmp_path) + "/Desktop/**/*"

    secondary, project = _detect_hierarchy_from_primary(symlink_path, pattern)

    # After matching tmp_path/Desktop/, remaining is Projects/MyApp/data
    # First part = Projects (secondary), second part = MyApp (project)
    assert secondary == "Projects"
    assert project == "MyApp"


def test_detect_hierarchy_from_primary_no_remaining_parts() -> None:
    """Test when pattern matches entire path (edge case)."""
    symlink_path = Path("/Users/me/Desktop")
    pattern = "/Users/*/Desktop"

    secondary, project = _detect_hierarchy_from_primary(symlink_path, pattern)

    # Fallback to parent name since no remaining parts
    assert secondary == "me"
    assert project == "Desktop"


def test_detect_hierarchy_from_primary_one_remaining_part() -> None:
    """Test when only one part remains after pattern match."""
    symlink_path = Path("/Users/me/Desktop/Tools")
    pattern = "/Users/*/Desktop/**/*"

    secondary, project = _detect_hierarchy_from_primary(symlink_path, pattern)

    # Only "Tools" remains → secondary = root, project = Tools
    assert secondary == "root"
    assert project == "Tools"


def test_classify_symlinks_auto_hierarchy_basic(tmp_path: Path) -> None:
    """Test basic auto-hierarchy classification with config."""
    scan_root = tmp_path
    target = tmp_path / "target_dir"
    target.mkdir()

    # Create directory structure: Desktop/Projects/ProjectAlpha/data
    (scan_root / "Desktop" / "Projects" / "ProjectAlpha").mkdir(parents=True)
    link1 = scan_root / "Desktop" / "Projects" / "ProjectAlpha" / "data"
    os.symlink(target, link1)

    # Create: Service/APIs/APIService/config
    (scan_root / "Service" / "APIs" / "APIService").mkdir(parents=True)
    link2 = scan_root / "Service" / "APIs" / "APIService" / "config"
    os.symlink(target, link2)

    # Simplified config: only Level 1 categories with patterns
    config = OrderedDict([
        ("Desktop", [f"{scan_root}/Desktop/**/*"]),
        ("Service", [f"{scan_root}/Service/**/*"]),
    ])

    symlinks = [
        SymlinkInfo(path=link1, name="data", target=target, is_broken=False),
        SymlinkInfo(path=link2, name="config", target=target, is_broken=False),
    ]

    result = classify_symlinks_auto_hierarchy(symlinks, config, scan_root=scan_root)

    # Verify structure
    assert "Desktop" in result
    assert "Service" in result

    # Desktop should have Projects as secondary
    assert "Projects" in result["Desktop"]
    assert len(result["Desktop"]["Projects"]) == 1

    desktop_item = result["Desktop"]["Projects"][0]
    assert desktop_item.primary_category == "Desktop"
    assert desktop_item.secondary_category == "Projects"
    assert desktop_item.project_name == "ProjectAlpha"

    # Service should have APIs as secondary
    assert "APIs" in result["Service"]
    assert len(result["Service"]["APIs"]) == 1

    service_item = result["Service"]["APIs"][0]
    assert service_item.primary_category == "Service"
    assert service_item.secondary_category == "APIs"
    assert service_item.project_name == "APIService"


def test_classify_symlinks_auto_hierarchy_unclassified(tmp_path: Path) -> None:
    """Test that unmatched symlinks go to unclassified."""
    scan_root = tmp_path
    target = tmp_path / "target_dir"
    target.mkdir()

    # Create symlink that won't match any pattern
    (scan_root / "RandomFolder").mkdir()
    link = scan_root / "RandomFolder" / "orphan"
    os.symlink(target, link)

    config = OrderedDict([
        ("Desktop", [f"{scan_root}/Desktop/**/*"]),
    ])

    symlinks = [
        SymlinkInfo(path=link, name="orphan", target=target, is_broken=False),
    ]

    result = classify_symlinks_auto_hierarchy(symlinks, config, scan_root=scan_root)

    # Should be in unclassified
    assert "unclassified" in result
    assert "unclassified" in result["unclassified"]
    assert len(result["unclassified"]["unclassified"]) == 1

    unclass_item = result["unclassified"]["unclassified"][0]
    assert unclass_item.primary_category == "unclassified"
    assert unclass_item.secondary_category == "unclassified"
    assert unclass_item.project_name == "orphan"


def test_classify_symlinks_auto_hierarchy_multiple_secondary(tmp_path: Path) -> None:
    """Test multiple secondary categories under same primary."""
    scan_root = tmp_path
    target = tmp_path / "target_dir"
    target.mkdir()

    # Create Desktop/Projects/ProjectA/data
    (scan_root / "Desktop" / "Projects" / "ProjectA").mkdir(parents=True)
    link1 = scan_root / "Desktop" / "Projects" / "ProjectA" / "data"
    os.symlink(target, link1)

    # Create Desktop/Tools/ToolX/config
    (scan_root / "Desktop" / "Tools" / "ToolX").mkdir(parents=True)
    link2 = scan_root / "Desktop" / "Tools" / "ToolX" / "config"
    os.symlink(target, link2)

    config = OrderedDict([
        ("Desktop", [f"{scan_root}/Desktop/**/*"]),
    ])

    symlinks = [
        SymlinkInfo(path=link1, name="data", target=target, is_broken=False),
        SymlinkInfo(path=link2, name="config", target=target, is_broken=False),
    ]

    result = classify_symlinks_auto_hierarchy(symlinks, config, scan_root=scan_root)

    # Desktop should have both Projects and Tools as secondary categories
    assert "Desktop" in result
    assert "Projects" in result["Desktop"]
    assert "Tools" in result["Desktop"]

    assert len(result["Desktop"]["Projects"]) == 1
    assert len(result["Desktop"]["Tools"]) == 1

    project_item = result["Desktop"]["Projects"][0]
    assert project_item.project_name == "ProjectA"

    tool_item = result["Desktop"]["Tools"][0]
    assert tool_item.project_name == "ToolX"


def test_classify_symlinks_auto_hierarchy_tilde_expansion(tmp_path: Path) -> None:
    """Test that ~ in patterns is expanded to home directory."""
    scan_root = Path.home() / "test_scan"
    target = tmp_path / "target_dir"
    target.mkdir()

    # Create structure under home
    test_dir = scan_root / "Desktop" / "Projects" / "MyProject"
    test_dir.mkdir(parents=True, exist_ok=True)
    link = test_dir / "data"

    try:
        os.symlink(target, link)

        # Config with ~ pattern
        config = OrderedDict([
            ("Desktop", ["~/test_scan/Desktop/**/*"]),
        ])

        symlinks = [
            SymlinkInfo(path=link, name="data", target=target, is_broken=False),
        ]

        result = classify_symlinks_auto_hierarchy(symlinks, config, scan_root=scan_root)

        # Should match and classify
        assert "Desktop" in result
        assert len(result["Desktop"]) > 0

    finally:
        # Cleanup
        if link.exists() or link.is_symlink():
            link.unlink()
        if test_dir.exists():
            import shutil
            shutil.rmtree(scan_root, ignore_errors=True)


def test_classify_symlinks_auto_hierarchy_deeply_nested(tmp_path: Path) -> None:
    """Test deeply nested paths extract correct levels."""
    scan_root = tmp_path
    target = tmp_path / "target_dir"
    target.mkdir()

    # Create: Desktop/Projects/MyApp/subdir1/subdir2/data
    deep_path = scan_root / "Desktop" / "Projects" / "MyApp" / "subdir1" / "subdir2"
    deep_path.mkdir(parents=True)
    link = deep_path / "data"
    os.symlink(target, link)

    config = OrderedDict([
        ("Desktop", [f"{scan_root}/Desktop/**/*"]),
    ])

    symlinks = [
        SymlinkInfo(path=link, name="data", target=target, is_broken=False),
    ]

    result = classify_symlinks_auto_hierarchy(symlinks, config, scan_root=scan_root)

    # Should extract first two levels after pattern match
    # After Desktop/, remaining = Projects/MyApp/subdir1/subdir2/data
    # secondary = Projects, project = MyApp
    assert "Desktop" in result
    assert "Projects" in result["Desktop"]

    item = result["Desktop"]["Projects"][0]
    assert item.secondary_category == "Projects"
    assert item.project_name == "MyApp"


def test_classify_symlinks_auto_hierarchy_backward_compat_project_field(tmp_path: Path) -> None:
    """Test that the 'project' field is set for backward compatibility."""
    scan_root = tmp_path
    target = tmp_path / "target_dir"
    target.mkdir()

    (scan_root / "Desktop" / "Projects" / "ProjectA").mkdir(parents=True)
    link = scan_root / "Desktop" / "Projects" / "ProjectA" / "data"
    os.symlink(target, link)

    config = OrderedDict([
        ("Desktop", [f"{scan_root}/Desktop/**/*"]),
    ])

    symlinks = [
        SymlinkInfo(path=link, name="data", target=target, is_broken=False),
    ]

    result = classify_symlinks_auto_hierarchy(symlinks, config, scan_root=scan_root)

    item = result["Desktop"]["Projects"][0]

    # Backward compat: project field should be set to primary_category
    assert item.project == "Desktop"
    assert item.primary_category == "Desktop"
