"""Test TUI table alignment fix - verify single table per group, not per row."""

from pathlib import Path
from unittest.mock import MagicMock, patch
from symlink_manager.ui.tui import _build_rows, _render_list
from symlink_manager.core.scanner import SymlinkInfo


def test_tui_renders_single_table_per_group():
    """Verify that TUI creates one table per group, not one per row."""

    # Create mock symlinks with different groups
    mock_symlinks = [
        SymlinkInfo(
            path=Path("/test/link1"),
            name="link1",
            target=Path("/test/target1"),
            is_broken=False,
            project="project-a"
        ),
        SymlinkInfo(
            path=Path("/test/link2"),
            name="link2",
            target=Path("/test/target2"),
            is_broken=False,
            project="project-a"
        ),
        SymlinkInfo(
            path=Path("/test/link3"),
            name="link3",
            target=Path("/test/target3"),
            is_broken=True,
            project="unclassified"
        ),
    ]

    # Build buckets
    buckets = {
        "project-a": [mock_symlinks[0], mock_symlinks[1]],
        "unclassified": [mock_symlinks[2]]
    }

    rows = _build_rows(buckets)
    item_row_indices = [idx for idx, r in enumerate(rows) if r.kind == "item"]

    # Mock console to capture print calls
    with patch('symlink_manager.ui.tui.console') as mock_console:
        mock_console.size.width = 120
        mock_console.size.height = 50
        mock_console.clear = MagicMock()
        mock_console.print = MagicMock()

        # Render the list
        _render_list(
            rows,
            cursor_item_pos=0,
            item_row_indices=item_row_indices,
            scan_path=Path("/test"),
            config_path=None
        )

        # Count how many times console.print was called
        print_calls = mock_console.print.call_args_list

        # Count Table objects printed (not Text objects for headers)
        from rich.table import Table
        table_print_calls = [
            call for call in print_calls
            if len(call[0]) > 0 and isinstance(call[0][0], Table)
        ]

        # Should have exactly 2 tables: one for project-a (2 items), one for unclassified (1 item)
        assert len(table_print_calls) == 2, (
            f"Expected 2 tables (one per group), got {len(table_print_calls)}. "
            "This means we're still creating one table per row!"
        )

        print("✓ TUI alignment fix verified: Single table per group, not per row")


def test_tui_table_has_consistent_columns():
    """Verify that tables have consistent column structure."""

    mock_symlinks = [
        SymlinkInfo(
            path=Path("/test/link1"),
            name="link1",
            target=Path("/test/target1"),
            is_broken=False,
            project="project-a"
        ),
    ]

    buckets = {"project-a": [mock_symlinks[0]]}
    rows = _build_rows(buckets)
    item_row_indices = [idx for idx, r in enumerate(rows) if r.kind == "item"]

    with patch('symlink_manager.ui.tui.console') as mock_console:
        mock_console.size.width = 120
        mock_console.size.height = 50
        mock_console.clear = MagicMock()
        mock_console.print = MagicMock()

        _render_list(
            rows,
            cursor_item_pos=0,
            item_row_indices=item_row_indices,
            scan_path=Path("/test"),
            config_path=None
        )

        print_calls = mock_console.print.call_args_list
        from rich.table import Table

        for call in print_calls:
            if len(call[0]) > 0 and isinstance(call[0][0], Table):
                table = call[0][0]
                # Verify table has exactly 3 columns
                assert len(table.columns) == 3, f"Expected 3 columns, got {len(table.columns)}"

                # Verify column names
                col_names = [col.header for col in table.columns]
                assert col_names == ["Name", "Target", "Status"], (
                    f"Expected ['Name', 'Target', 'Status'], got {col_names}"
                )

        print("✓ TUI tables have consistent 3-column structure")


if __name__ == "__main__":
    test_tui_renders_single_table_per_group()
    test_tui_table_has_consistent_columns()
    print("\n✅ All TUI alignment tests passed!")
