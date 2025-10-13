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

    # Create various symlinks
    (scan_dir / "python3").symlink_to("/usr/bin/python3")
    (scan_dir / "data").symlink_to("/tmp/data")

    # Scan without filtering
    symlinks = scan_symlinks(
        scan_path=scan_dir,
        exclude_patterns=None
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
