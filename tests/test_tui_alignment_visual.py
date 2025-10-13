"""Visual alignment assertions for the TUI table output.

These tests capture the rendered table text and assert that the
vertical separators line up for every rendered data row. This helps
catch subtle width-budget mistakes that don't show up when only
counting printed Table objects.
"""

from pathlib import Path
from typing import List, Tuple

import pytest
from rich.console import Console
from rich.text import Text

from symlink_manager.core.scanner import SymlinkInfo
from symlink_manager.ui.tui import _build_rows, _render_list


def _capture_render(rows, cursor_item_pos, item_row_indices, width: int, height: int) -> str:
    """Patch the module console to a recording Console and capture text output."""
    from unittest.mock import patch

    console = Console(record=True, force_terminal=True, width=width, height=height, color_system=None)

    with patch("symlink_manager.ui.tui.console", console):
        _render_list(
            rows,
            cursor_item_pos=cursor_item_pos,
            item_row_indices=item_row_indices,
            scan_path=Path("/scan"),
            config_path=None,
        )
        return console.export_text(clear=False)


def _separator_columns(lines: List[str]) -> List[Tuple[int, int, int, int]]:
    """Return indices of the first four vertical separators on each line.

    The SIMPLE box drawing uses Unicode box characters (e.g., '│'). We
    locate them and ensure that each content line uses the same column
    indices for the separators.
    """
    seps_per_line: List[Tuple[int, int, int, int]] = []
    for line in lines:
        # Only check lines that look like table rows (contain vertical bars)
        positions = [i for i, ch in enumerate(line) if ch == "│"]
        if len(positions) >= 4:
            seps_per_line.append(tuple(positions[:4]))
    return seps_per_line


@pytest.mark.parametrize("term_width", [60, 80, 100, 120])
def test_table_separators_align_across_rows(term_width):
    # Create mock rows with long names/targets to trigger truncation
    items = []
    for i in range(15):
        name = f"very-long-name-{i}-with-some-extra-characters-to-truncate"
        target = f"/deep/path/to/somewhere/that/is/also/quite/long/target-{i}.txt"
        items.append(
            SymlinkInfo(
                path=Path(f"/x/link-{i}"),
                name=name,
                target=Path(target),
                is_broken=(i % 7 == 0),
                project="group-a",
            )
        )

    buckets = {"group-a": items, "unclassified": items[:3]}
    rows = _build_rows(buckets)
    item_row_indices = [idx for idx, r in enumerate(rows) if r.kind == "item"]

    text = _capture_render(rows, cursor_item_pos=0, item_row_indices=item_row_indices, width=term_width, height=40)
    lines = text.splitlines()

    seps = _separator_columns(lines)
    # There should be many content lines with separators to compare
    assert len(seps) >= 5, "Expected multiple table lines with separators to analyze alignment"

    # All separator tuples in a contiguous table block should be identical
    first = seps[0]
    for idx, tpl in enumerate(seps[1:], start=1):
        assert tpl == first, (
            f"Vertical separators misaligned on line index {idx}: {tpl} != {first}.\n"
            f"Rendered text:\n{text}"
        )


def test_header_then_table_alignment_constant_width():
    # Minimal case: one group header + a few items
    items = [
        SymlinkInfo(path=Path("/p/a"), name="alpha", target=Path("/x/y/z"), is_broken=False, project="proj"),
        SymlinkInfo(path=Path("/p/b"), name="beta", target=Path("/x/y/z"), is_broken=True, project="proj"),
        SymlinkInfo(path=Path("/p/c"), name="gamma", target=Path("/x/y/z"), is_broken=False, project="proj"),
    ]
    rows = _build_rows({"proj": items})
    item_row_indices = [idx for idx, r in enumerate(rows) if r.kind == "item"]

    text = _capture_render(rows, cursor_item_pos=0, item_row_indices=item_row_indices, width=80, height=30)
    lines = text.splitlines()
    seps = _separator_columns(lines)
    assert seps, "No table separator lines found in captured output"
    first = seps[0]
    for tpl in seps[1:]:
        assert tpl == first, "Separator columns vary between lines (header/table interaction bug?)"

