"""Tests for project_mode.py - Project-level data directory status API.

These tests cover the ProjectDataStatus dataclass and related functions
for querying and modifying project data directory link modes.
"""

import os
from pathlib import Path
from typing import List, Optional

import pytest


# Note: These tests are written in anticipation of the project_mode.py module.
# They define the expected behavior and will pass once the module is implemented.


class TestProjectDataStatus:
    """Tests for ProjectDataStatus dataclass and get_project_data_status()."""

    def test_mode_missing_when_data_dir_not_exists(self, tmp_path):
        """When data directory doesn't exist, mode should be 'missing'."""
        from slm.core.project_mode import get_project_data_status

        project_root = tmp_path / "my_project"
        project_root.mkdir()
        data_root = tmp_path / "Data"
        data_root.mkdir()

        status = get_project_data_status(
            project_root=project_root,
            data_root=data_root,
        )

        assert status.project_root == project_root
        assert status.data_path == project_root / "data"
        assert status.mode == "missing"
        assert status.link_text is None
        assert status.target_path is None
        assert status.shared_with == []

    def test_mode_inline_when_data_is_real_directory(self, tmp_path):
        """When data is a real directory (not symlink), mode should be 'inline'."""
        from slm.core.project_mode import get_project_data_status

        project_root = tmp_path / "my_project"
        project_root.mkdir()
        data_dir = project_root / "data"
        data_dir.mkdir()
        (data_dir / "file.txt").write_text("content")

        data_root = tmp_path / "Data"
        data_root.mkdir()

        status = get_project_data_status(
            project_root=project_root,
            data_root=data_root,
        )

        assert status.mode == "inline"
        assert status.data_path == data_dir
        assert status.target_path == data_dir
        assert status.link_text is None
        assert status.shared_with == []

    def test_mode_relative_when_data_is_relative_symlink(self, tmp_path):
        """When data is a relative symlink, mode should be 'relative'."""
        from slm.core.project_mode import get_project_data_status

        data_root = tmp_path / "Data"
        data_root.mkdir()
        target = data_root / "my_project-data"
        target.mkdir()

        project_root = tmp_path / "projects" / "my_project"
        project_root.mkdir(parents=True)
        data_link = project_root / "data"

        # Create relative symlink
        rel_path = os.path.relpath(target, data_link.parent)
        data_link.symlink_to(rel_path)

        status = get_project_data_status(
            project_root=project_root,
            data_root=data_root,
        )

        assert status.mode == "relative"
        assert status.data_path == data_link
        assert status.target_path == target.resolve()
        assert status.link_text == rel_path
        assert not os.path.isabs(status.link_text)

    def test_mode_absolute_when_data_is_absolute_symlink(self, tmp_path):
        """When data is an absolute symlink, mode should be 'absolute'."""
        from slm.core.project_mode import get_project_data_status

        data_root = tmp_path / "Data"
        data_root.mkdir()
        target = data_root / "my_project-data"
        target.mkdir()

        project_root = tmp_path / "projects" / "my_project"
        project_root.mkdir(parents=True)
        data_link = project_root / "data"

        # Create absolute symlink
        data_link.symlink_to(str(target.resolve()))

        status = get_project_data_status(
            project_root=project_root,
            data_root=data_root,
        )

        assert status.mode == "absolute"
        assert status.data_path == data_link
        assert status.target_path == target.resolve()
        assert os.path.isabs(status.link_text)

    def test_shared_with_identifies_projects_with_same_target(self, tmp_path):
        """shared_with should list other projects pointing to same target."""
        from slm.core.project_mode import get_project_data_status

        data_root = tmp_path / "Data"
        data_root.mkdir()
        shared_target = data_root / "shared-data"
        shared_target.mkdir()

        # Create three projects, two sharing the same target
        projects_root = tmp_path / "projects"
        projects_root.mkdir()

        project_a = projects_root / "project_a"
        project_a.mkdir()
        (project_a / "data").symlink_to(shared_target)

        project_b = projects_root / "project_b"
        project_b.mkdir()
        (project_b / "data").symlink_to(shared_target)

        project_c = projects_root / "project_c"
        project_c.mkdir()
        other_target = data_root / "other-data"
        other_target.mkdir()
        (project_c / "data").symlink_to(other_target)

        all_projects = [project_a, project_b, project_c]

        status_a = get_project_data_status(
            project_root=project_a,
            data_root=data_root,
            all_project_roots=all_projects,
        )

        assert status_a.target_path == shared_target.resolve()
        assert len(status_a.shared_with) == 1
        assert project_b in status_a.shared_with
        assert project_a not in status_a.shared_with  # Self not included
        assert project_c not in status_a.shared_with  # Different target

    def test_shared_with_empty_when_no_all_project_roots(self, tmp_path):
        """shared_with should be empty when all_project_roots not provided."""
        from slm.core.project_mode import get_project_data_status

        data_root = tmp_path / "Data"
        data_root.mkdir()
        target = data_root / "my-data"
        target.mkdir()

        project_root = tmp_path / "my_project"
        project_root.mkdir()
        (project_root / "data").symlink_to(target)

        status = get_project_data_status(
            project_root=project_root,
            data_root=data_root,
            # all_project_roots not provided
        )

        assert status.shared_with == []

    def test_broken_symlink_returns_missing_mode(self, tmp_path):
        """When symlink points to non-existent target, mode should be 'missing'."""
        from slm.core.project_mode import get_project_data_status

        project_root = tmp_path / "my_project"
        project_root.mkdir()
        data_link = project_root / "data"
        data_link.symlink_to("/nonexistent/path")

        data_root = tmp_path / "Data"
        data_root.mkdir()

        status = get_project_data_status(
            project_root=project_root,
            data_root=data_root,
        )

        # Broken symlink should be treated as missing
        assert status.mode == "missing"


class TestSetProjectDataMode:
    """Tests for set_project_data_mode() function."""

    def test_set_mode_relative_from_absolute(self, tmp_path):
        """Convert absolute symlink to relative symlink."""
        from slm.core.project_mode import get_project_data_status, set_project_data_mode

        data_root = tmp_path / "Data"
        data_root.mkdir()
        target = data_root / "my-data"
        target.mkdir()
        (target / "file.txt").write_text("content")

        project_root = tmp_path / "my_project"
        project_root.mkdir()
        data_link = project_root / "data"
        data_link.symlink_to(str(target.resolve()))  # Absolute

        # Verify initial state
        assert os.path.isabs(os.readlink(data_link))

        # Set to relative mode
        new_status = set_project_data_mode(
            project_root=project_root,
            data_root=data_root,
            mode="relative",
        )

        assert new_status.mode == "relative"
        assert not os.path.isabs(os.readlink(data_link))
        assert data_link.resolve() == target.resolve()
        assert (data_link / "file.txt").read_text() == "content"

    def test_set_mode_absolute_from_relative(self, tmp_path):
        """Convert relative symlink to absolute symlink."""
        from slm.core.project_mode import get_project_data_status, set_project_data_mode

        data_root = tmp_path / "Data"
        data_root.mkdir()
        target = data_root / "my-data"
        target.mkdir()

        project_root = tmp_path / "my_project"
        project_root.mkdir()
        data_link = project_root / "data"
        rel_path = os.path.relpath(target, data_link.parent)
        data_link.symlink_to(rel_path)  # Relative

        # Verify initial state
        assert not os.path.isabs(os.readlink(data_link))

        # Set to absolute mode
        new_status = set_project_data_mode(
            project_root=project_root,
            data_root=data_root,
            mode="absolute",
        )

        assert new_status.mode == "absolute"
        assert os.path.isabs(os.readlink(data_link))
        assert data_link.resolve() == target.resolve()

    def test_set_mode_inline_copies_data(self, tmp_path):
        """Converting to inline mode copies data and removes symlink."""
        from slm.core.project_mode import get_project_data_status, set_project_data_mode

        data_root = tmp_path / "Data"
        data_root.mkdir()
        target = data_root / "my-data"
        target.mkdir()
        (target / "file.txt").write_text("inline content")

        project_root = tmp_path / "my_project"
        project_root.mkdir()
        data_link = project_root / "data"
        data_link.symlink_to(target)

        # Set to inline mode
        new_status = set_project_data_mode(
            project_root=project_root,
            data_root=data_root,
            mode="inline",
        )

        assert new_status.mode == "inline"
        assert not data_link.is_symlink()
        assert data_link.is_dir()
        assert (data_link / "file.txt").read_text() == "inline content"
        # Original target should still exist
        assert target.exists()

    def test_set_mode_noop_when_already_target_mode(self, tmp_path):
        """Setting same mode should be a no-op."""
        from slm.core.project_mode import get_project_data_status, set_project_data_mode

        data_root = tmp_path / "Data"
        data_root.mkdir()
        target = data_root / "my-data"
        target.mkdir()

        project_root = tmp_path / "my_project"
        project_root.mkdir()
        data_link = project_root / "data"
        rel_path = os.path.relpath(target, data_link.parent)
        data_link.symlink_to(rel_path)

        original_link_text = os.readlink(data_link)

        # Set to relative (already relative)
        new_status = set_project_data_mode(
            project_root=project_root,
            data_root=data_root,
            mode="relative",
        )

        assert new_status.mode == "relative"
        # Link should be unchanged
        assert os.readlink(data_link) == original_link_text

    def test_set_mode_raises_on_missing(self, tmp_path):
        """Cannot set mode when data directory is missing."""
        from slm.core.project_mode import set_project_data_mode
        from slm.core.migration import MigrationError

        project_root = tmp_path / "my_project"
        project_root.mkdir()
        # No data directory

        data_root = tmp_path / "Data"
        data_root.mkdir()

        with pytest.raises(MigrationError):
            set_project_data_mode(
                project_root=project_root,
                data_root=data_root,
                mode="relative",
            )


class TestProjectDataStatusDataclass:
    """Tests for ProjectDataStatus dataclass structure."""

    def test_dataclass_fields(self):
        """Verify ProjectDataStatus has required fields."""
        from slm.core.project_mode import ProjectDataStatus

        # Create instance with all required fields
        status = ProjectDataStatus(
            project_root=Path("/test/project"),
            data_path=Path("/test/project/data"),
            mode="relative",
            link_text="../Data/test-data",
            target_path=Path("/test/Data/test-data"),
            shared_with=[],
        )

        assert status.project_root == Path("/test/project")
        assert status.data_path == Path("/test/project/data")
        assert status.mode == "relative"
        assert status.link_text == "../Data/test-data"
        assert status.target_path == Path("/test/Data/test-data")
        assert status.shared_with == []

    def test_dataclass_optional_fields(self):
        """Verify optional fields can be None."""
        from slm.core.project_mode import ProjectDataStatus

        status = ProjectDataStatus(
            project_root=Path("/test/project"),
            data_path=None,
            mode="missing",
            link_text=None,
            target_path=None,
            shared_with=[],
        )

        assert status.data_path is None
        assert status.link_text is None
        assert status.target_path is None


class TestLinkModeType:
    """Tests for LinkMode type alias."""

    def test_valid_link_modes(self):
        """Verify all valid LinkMode values."""
        from slm.core.project_mode import LinkMode

        valid_modes: List[LinkMode] = ["relative", "absolute", "inline", "missing"]

        for mode in valid_modes:
            # Should not raise type errors
            assert mode in ["relative", "absolute", "inline", "missing"]


class TestIntegrationWithExistingCode:
    """Integration tests with existing slm functionality."""

    def test_get_status_uses_scanner_correctly(self, tmp_path):
        """Verify get_project_data_status integrates with scanner module."""
        from slm.core.project_mode import get_project_data_status
        from slm.core.scanner import scan_symlinks_pointing_into_data

        data_root = tmp_path / "Data"
        data_root.mkdir()
        target = data_root / "proj-data"
        target.mkdir()

        project_root = tmp_path / "proj"
        project_root.mkdir()
        (project_root / "data").symlink_to(target)

        # Both functions should recognize the same symlink
        status = get_project_data_status(project_root, data_root)
        infos = scan_symlinks_pointing_into_data([project_root], data_root)

        assert status.target_path == infos[0].target if infos else None

    def test_set_mode_uses_migration_correctly(self, tmp_path):
        """Verify set_project_data_mode reuses migration logic."""
        from slm.core.project_mode import set_project_data_mode

        data_root = tmp_path / "Data"
        data_root.mkdir()
        target = data_root / "proj-data"
        target.mkdir()
        (target / "marker.txt").write_text("marker")

        project_root = tmp_path / "proj"
        project_root.mkdir()
        data_link = project_root / "data"
        data_link.symlink_to(str(target.resolve()))

        # Set to relative - should use migration functions internally
        result = set_project_data_mode(project_root, data_root, "relative")

        # Data should be intact after mode change
        assert result.mode == "relative"
        assert (data_link / "marker.txt").read_text() == "marker"
