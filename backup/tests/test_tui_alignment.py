"""Test TUI data structures - verify _build_rows creates correct row structure."""

from pathlib import Path
from symlink_manager.ui.tui import _build_rows, _Row
from symlink_manager.core.scanner import SymlinkInfo


def test_build_rows_creates_headers_before_groups():
    """Verify that _build_rows creates header rows before each group."""

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

    # Verify structure:
    # [0] header: project-a
    # [1] item: link1
    # [2] item: link2
    # [3] header: unclassified
    # [4] item: link3

    assert len(rows) == 5, f"Expected 5 rows (2 headers + 3 items), got {len(rows)}"

    # Verify first group
    assert rows[0].kind == "primary_header", f"Row 0 should be primary_header, got {rows[0].kind}"
    assert rows[0].title == "project-a", f"Row 0 title should be 'project-a', got {rows[0].title}"

    assert rows[1].kind == "item", f"Row 1 should be item, got {rows[1].kind}"
    assert rows[1].item.name == "link1", f"Row 1 item name should be 'link1', got {rows[1].item.name}"

    assert rows[2].kind == "item", f"Row 2 should be item, got {rows[2].kind}"
    assert rows[2].item.name == "link2", f"Row 2 item name should be 'link2', got {rows[2].item.name}"

    # Verify second group
    assert rows[3].kind == "primary_header", f"Row 3 should be primary_header, got {rows[3].kind}"
    assert rows[3].title == "unclassified", f"Row 3 title should be 'unclassified', got {rows[3].title}"

    assert rows[4].kind == "item", f"Row 4 should be item, got {rows[4].kind}"
    assert rows[4].item.name == "link3", f"Row 4 item name should be 'link3', got {rows[4].item.name}"

    print("✓ _build_rows creates correct row structure with headers before groups")


def test_build_rows_unclassified_appears_last():
    """Verify that 'unclassified' group always appears at the end."""

    mock_symlinks = [
        SymlinkInfo(
            path=Path("/test/link1"),
            name="link1",
            target=Path("/test/target1"),
            is_broken=False,
            project="unclassified"
        ),
        SymlinkInfo(
            path=Path("/test/link2"),
            name="link2",
            target=Path("/test/target2"),
            is_broken=False,
            project="zebra-project"
        ),
        SymlinkInfo(
            path=Path("/test/link3"),
            name="link3",
            target=Path("/test/target3"),
            is_broken=False,
            project="alpha-project"
        ),
    ]

    buckets = {
        "unclassified": [mock_symlinks[0]],
        "zebra-project": [mock_symlinks[1]],
        "alpha-project": [mock_symlinks[2]],
    }

    rows = _build_rows(buckets)

    # Find primary header rows
    headers = [r for r in rows if r.kind == "primary_header"]

    # The last header should be "unclassified"
    assert len(headers) > 0, "Expected at least one header row"
    assert headers[-1].title == "unclassified", (
        f"Last header should be 'unclassified', got '{headers[-1].title}'"
    )

    # The other headers should not be "unclassified"
    for header in headers[:-1]:
        assert header.title != "unclassified", (
            f"Found 'unclassified' header before the last position: {[h.title for h in headers]}"
        )

    print("✓ _build_rows ensures 'unclassified' appears last")


def test_build_rows_row_kind_is_correct():
    """Verify that row.kind is set correctly ('header' vs 'item')."""

    mock_symlinks = [
        SymlinkInfo(
            path=Path("/test/link1"),
            name="link1",
            target=Path("/test/target1"),
            is_broken=False,
            project="test-project"
        ),
    ]

    buckets = {"test-project": [mock_symlinks[0]]}

    rows = _build_rows(buckets)

    # Should have 1 header + 1 item
    assert len(rows) == 2, f"Expected 2 rows, got {len(rows)}"

    # First should be primary_header
    assert rows[0].kind == "primary_header", f"Row 0 should be 'primary_header', got '{rows[0].kind}'"
    assert rows[0].item is None, "Header row should have item=None"

    # Second should be item
    assert rows[1].kind == "item", f"Row 1 should be 'item', got '{rows[1].kind}'"
    assert rows[1].item is not None, "Item row should have non-None item"
    assert isinstance(rows[1].item, SymlinkInfo), "Item should be a SymlinkInfo object"

    print("✓ _build_rows sets row.kind correctly")


if __name__ == "__main__":
    test_build_rows_creates_headers_before_groups()
    test_build_rows_unclassified_appears_last()
    test_build_rows_row_kind_is_correct()
    print("\n✅ All TUI data structure tests passed!")
