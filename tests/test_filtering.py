"""Tests for filtering functionality."""

from pathlib import Path
import tempfile
import os

from symlink_manager.core.scanner import scan_symlinks
from symlink_manager.core.filter_config import (
    load_filter_config,
    FilterRules,
    DEFAULT_EXCLUDE_PATTERNS,
)


def test_filtering_excludes_python_symlinks(tmp_path: Path):
    """Test that python* symlinks are filtered out."""
    # Create test directory structure
    scan_dir = tmp_path / "test_scan"
    scan_dir.mkdir()

    # Create various symlinks
    (scan_dir / "python3").symlink_to("/usr/bin/python3")
    (scan_dir / "python3.11").symlink_to("/usr/bin/python3.11")
    (scan_dir / "pip").symlink_to("/usr/bin/pip")
    (scan_dir / "data").symlink_to("/tmp/data")
    (scan_dir / "custom").symlink_to("/tmp/custom")

    # Scan with default exclude patterns
    symlinks = scan_symlinks(
        scan_path=scan_dir,
        exclude_patterns=DEFAULT_EXCLUDE_PATTERNS
    )

    # Should only find data and custom, not python3/python3.11/pip
    names = {s.name for s in symlinks}
    assert "data" in names
    assert "custom" in names
    assert "python3" not in names
    assert "python3.11" not in names
    assert "pip" not in names


def test_filtering_no_patterns_shows_all(tmp_path: Path):
    """Test that no filtering shows all symlinks."""
    # Create test directory structure
    scan_dir = tmp_path / "test_scan"
    scan_dir.mkdir()

    # Create target directories
    target1 = tmp_path / "target1"
    target1.mkdir()
    target2 = tmp_path / "target2"
    target2.mkdir()

    # Create various symlinks
    (scan_dir / "python3").symlink_to(target1)
    (scan_dir / "data").symlink_to(target2)

    # Scan without filtering (but note: directories_only defaults to True)
    symlinks = scan_symlinks(
        scan_path=scan_dir,
        exclude_patterns=None,
        directories_only=False,  # Disable all type filtering
        filter_garbled=False,    # Disable garbled filtering
    )

    # Should find all symlinks
    names = {s.name for s in symlinks}
    assert "python3" in names
    assert "data" in names
    assert len(names) == 2


def test_filter_rules_pattern_matching():
    """Test FilterRules pattern matching logic."""
    rules = FilterRules(
        include_patterns=[],
        exclude_patterns=["python*", "pip*"],
        ignore_case=False,
        use_regex=False,
    )

    # Should exclude matches
    assert not rules.should_include("python3")
    assert not rules.should_include("python3.11")
    assert not rules.should_include("pip")
    assert not rules.should_include("pip3")

    # Should include non-matches
    assert rules.should_include("data")
    assert rules.should_include("custom")
    assert rules.should_include("myapp")


def test_filter_rules_include_overrides_exclude():
    """Test that include patterns override exclude patterns."""
    rules = FilterRules(
        include_patterns=["python3.11"],  # Explicitly include this one
        exclude_patterns=["python*"],      # But exclude python* in general
        ignore_case=False,
        use_regex=False,
    )

    # python3.11 should be included despite matching exclude pattern
    assert rules.should_include("python3.11")

    # Other python* should still be excluded
    assert not rules.should_include("python3")
    assert not rules.should_include("python")


def test_load_filter_config_default_patterns_when_no_file():
    """Test that default patterns are used when no config file exists."""
    # Try to load from non-existent path
    rules = load_filter_config(Path("/nonexistent/filter.yml"))

    # Should return default exclude patterns
    assert rules.exclude_patterns == DEFAULT_EXCLUDE_PATTERNS
    assert rules.include_patterns == []


def test_default_exclude_patterns_comprehensive():
    """Test that all expected patterns are in defaults."""
    expected_patterns = [
        "python*",
        "pip*",
        "node*",
        "npm*",
        "ruby*",
        "gem*",
        ".git",
        "node_modules",
        "__pycache__",
        ".venv",
        "venv",
    ]

    for pattern in expected_patterns:
        assert pattern in DEFAULT_EXCLUDE_PATTERNS


def test_directories_only_filter(tmp_path: Path):
    """Test that only directory symlinks are included when directories_only=True."""
    # Create directory and file targets
    dir_target = tmp_path / "target_dir"
    dir_target.mkdir()
    file_target = tmp_path / "target_file.txt"
    file_target.write_text("content")

    # Create symlinks
    dir_link = tmp_path / "link_to_dir"
    dir_link.symlink_to(dir_target)
    file_link = tmp_path / "link_to_file"
    file_link.symlink_to(file_target)

    # Scan with directories_only=True (default)
    results = scan_symlinks(tmp_path, directories_only=True, filter_garbled=False, exclude_patterns=None)

    # Should only find dir_link, not file_link
    names = {s.name for s in results}
    assert "link_to_dir" in names
    assert "link_to_file" not in names
    assert len(names) == 1


def test_directories_only_disabled(tmp_path: Path):
    """Test that both file and directory symlinks are included when directories_only=False."""
    # Create directory and file targets
    dir_target = tmp_path / "target_dir"
    dir_target.mkdir()
    file_target = tmp_path / "target_file.txt"
    file_target.write_text("content")

    # Create symlinks
    dir_link = tmp_path / "link_to_dir"
    dir_link.symlink_to(dir_target)
    file_link = tmp_path / "link_to_file"
    file_link.symlink_to(file_target)

    # Scan with directories_only=False
    results = scan_symlinks(tmp_path, directories_only=False, filter_garbled=False, exclude_patterns=None)

    # Should find both links
    names = {s.name for s in results}
    assert "link_to_dir" in names
    assert "link_to_file" in names
    assert len(names) == 2


def test_directories_only_with_broken_links(tmp_path: Path):
    """Test that broken symlinks are still included (can't determine if they point to dir or file)."""
    # Create a directory target
    dir_target = tmp_path / "target_dir"
    dir_target.mkdir()

    # Create working and broken symlinks
    working_link = tmp_path / "link_working"
    working_link.symlink_to(dir_target)

    broken_link = tmp_path / "link_broken"
    broken_link.symlink_to(tmp_path / "nonexistent")

    # Scan with directories_only=True
    results = scan_symlinks(tmp_path, directories_only=True, filter_garbled=False, exclude_patterns=None)

    # Should find both (broken links are included since we can't check type)
    names = {s.name for s in results}
    assert "link_working" in names
    assert "link_broken" in names


def test_garbled_name_filter(tmp_path: Path):
    """Test that garbled names are filtered when filter_garbled=True."""
    # Create target
    target = tmp_path / "target"
    target.mkdir()

    # Normal name
    good_link = tmp_path / "good_link"
    good_link.symlink_to(target)

    # Try to create garbled name (with replacement character)
    # Note: Some filesystems may not allow creating this
    try:
        bad_link = tmp_path / "bad\ufffdlink"
        bad_link.symlink_to(target)
        garbled_created = True
    except (OSError, ValueError):
        garbled_created = False

    # Scan with filter_garbled=True (default)
    results = scan_symlinks(tmp_path, filter_garbled=True, directories_only=False, exclude_patterns=None)

    # Should only find good_link
    names = {s.name for s in results}
    assert "good_link" in names

    if garbled_created:
        assert "bad\ufffdlink" not in names


def test_garbled_name_filter_disabled(tmp_path: Path):
    """Test that garbled names are included when filter_garbled=False."""
    # Create target
    target = tmp_path / "target"
    target.mkdir()

    # Normal name
    good_link = tmp_path / "good_link"
    good_link.symlink_to(target)

    # Try to create garbled name
    try:
        bad_link = tmp_path / "bad\ufffdlink"
        bad_link.symlink_to(target)
        garbled_created = True
    except (OSError, ValueError):
        garbled_created = False

    # Scan with filter_garbled=False
    results = scan_symlinks(tmp_path, filter_garbled=False, directories_only=False, exclude_patterns=None)

    # Should find good_link
    names = {s.name for s in results}
    assert "good_link" in names

    # If garbled was created, should also find it
    if garbled_created:
        assert "bad\ufffdlink" in names


def test_combined_filters(tmp_path: Path):
    """Test directories_only + garbled + pattern exclusion together."""
    # Create various targets
    dir1 = tmp_path / "dir1"
    dir1.mkdir()
    file1 = tmp_path / "file1.txt"
    file1.write_text("x")

    # Create symlinks
    (tmp_path / "data").symlink_to(dir1)  # dir, good name -> KEEP
    (tmp_path / "python3").symlink_to(dir1)  # dir, excluded pattern -> FILTER
    (tmp_path / "link.txt").symlink_to(file1)  # file -> FILTER

    results = scan_symlinks(
        tmp_path,
        exclude_patterns=["python*"],
        directories_only=True,
        filter_garbled=True
    )

    # Should only find "data"
    names = {s.name for s in results}
    assert "data" in names
    assert "python3" not in names  # Excluded by pattern
    assert "link.txt" not in names  # Excluded as file
    assert len(names) == 1


def test_filter_rules_default_values():
    """Test that FilterRules has correct default values for new fields."""
    rules = FilterRules(
        include_patterns=[],
        exclude_patterns=[],
    )

    assert rules.directories_only is True
    assert rules.filter_garbled is True
