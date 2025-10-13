from __future__ import annotations

"""Interactive TUI (Task-4) using Rich for rendering.

Capabilities (read-only for MVP):
- Display symlinks grouped by project (classified first; "unclassified" last)
- Show name, current target, and status (green OK, red BROKEN)
- Keyboard navigation: Up/Down (or k/j), Enter to view details, q/Esc to quit
- Scrollable viewport for large lists (100+ items)
- Adaptive column widths based on terminal size
- Scroll indicators when more items exist above/below viewport
- Integrates with scanner + classifier modules

Notes:
- Input handling uses raw terminal mode (termios) to keep dependencies minimal
- Rendering uses Rich Console and Tables; full-screen re-render per keypress
- Only renders visible items for performance with large lists
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import sys
import termios
import tty

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.rule import Rule

from ..core.scanner import SymlinkInfo, scan_symlinks
from ..core.classifier import (
    classify_symlinks,
    load_markdown_config,
)


console = Console()


# ---- Key handling -----------------------------------------------------------

class _RawMode:
    def __init__(self, fd: int) -> None:
        self.fd = fd
        self._orig: Optional[list[int]] = None

    def __enter__(self):
        self._orig = termios.tcgetattr(self.fd)
        tty.setraw(self.fd)
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._orig is not None:
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self._orig)


def _read_key() -> str:
    """Read a single key (including arrow sequences) from stdin (raw mode).

    Returns symbolic names: 'UP', 'DOWN', 'ENTER', 'ESC', single characters like 'q'.
    """
    ch1 = sys.stdin.read(1)
    if ch1 == "\x1b":  # ESC or sequence
        # Peek next two to distinguish ESC vs arrows
        seq = sys.stdin.read(1)
        if not seq:
            return "ESC"
        if seq == "[":
            code = sys.stdin.read(1)
            if code == "A":
                return "UP"
            if code == "B":
                return "DOWN"
            if code == "C":
                return "RIGHT"
            if code == "D":
                return "LEFT"
        return "ESC"
    if ch1 in ("\r", "\n"):
        return "ENTER"
    return ch1


# ---- View model -------------------------------------------------------------

@dataclass
class _Row:
    kind: str  # 'header' | 'item'
    title: Optional[str] = None
    project: Optional[str] = None
    item: Optional[SymlinkInfo] = None


def _build_rows(buckets: Dict[str, List[SymlinkInfo]]) -> List[_Row]:
    """Flatten buckets into a list of rows with headers before each group.

    Ensures 'unclassified' group appears at the end.
    """
    rows: list[_Row] = []
    keys: List[str] = list(k for k in buckets.keys() if k != "unclassified")
    if "unclassified" in buckets:
        keys.append("unclassified")

    for proj in keys:
        rows.append(_Row(kind="header", title=proj))
        for item in buckets.get(proj, []):
            rows.append(_Row(kind="item", project=proj, item=item))
    return rows


def _count_items(rows: List[_Row]) -> int:
    return sum(1 for r in rows if r.kind == "item")


def _first_selectable_index(rows: List[_Row]) -> int:
    for idx, r in enumerate(rows):
        if r.kind == "item":
            return idx
    return 0


def _move_cursor(rows: List[_Row], current: int, delta: int) -> int:
    """Move to next selectable 'item' row, skipping headers."""
    if not rows:
        return 0
    idx = current
    step = 1 if delta >= 0 else -1
    remaining = abs(delta)
    while remaining > 0:
        nxt = idx + step
        # Clamp within bounds
        nxt = max(0, min(len(rows) - 1, nxt))
        # If no movement possible, break
        if nxt == idx:
            break
        idx = nxt
        if rows[idx].kind == "item":
            remaining -= 1
    # Ensure we land on an item; if header, keep moving in same direction
    while 0 <= idx < len(rows) and rows[idx].kind != "item":
        nxt = idx + step
        if nxt < 0 or nxt >= len(rows):
            break
        idx = nxt
    return idx


# ---- Rendering --------------------------------------------------------------

def _calculate_viewport_size() -> int:
    """Calculate how many item rows can fit in the terminal viewport.

    Reserves space for:
    - Header (1 line)
    - Info line (1 line)
    - Help line (1 line)
    - Rule (1 line)
    - Scroll indicators (2 lines max)
    - Footer help (1 line)
    - Some padding (2 lines)
    """
    terminal_height = console.size.height
    reserved_lines = 9
    return max(5, terminal_height - reserved_lines)


def _calculate_visible_range(
    rows: List[_Row],
    cursor_item_pos: int,
    item_row_indices: List[int],
    viewport_size: int
) -> Tuple[int, int]:
    """Calculate which rows should be visible given cursor position and viewport size.

    Returns (start_row_index, end_row_index) inclusive range.
    Ensures cursor is always visible and tries to keep it centered.
    """
    if not item_row_indices:
        return (0, 0)

    total_items = len(item_row_indices)
    if total_items <= viewport_size:
        # All items fit, show everything
        return (0, len(rows) - 1)

    # Calculate ideal window centered on cursor
    cursor_abs_row = item_row_indices[cursor_item_pos]

    # Find how many items are visible (accounting for headers)
    # Strategy: center cursor in viewport
    half_viewport = viewport_size // 2

    # Find start_item_pos
    start_item_pos = max(0, cursor_item_pos - half_viewport)
    end_item_pos = min(total_items - 1, start_item_pos + viewport_size - 1)

    # Adjust if we're at the end
    if end_item_pos == total_items - 1:
        start_item_pos = max(0, end_item_pos - viewport_size + 1)

    # Convert item positions to absolute row indices
    start_row = item_row_indices[start_item_pos]
    end_row = item_row_indices[end_item_pos]

    # Include headers for visible items by scanning backwards from start_row
    for i in range(start_row - 1, -1, -1):
        if rows[i].kind == "header":
            start_row = i
            break

    return (start_row, end_row)


def _truncate_text(text: str, max_width: int, suffix: str = "…") -> str:
    """Truncate text to max_width, adding suffix if truncated."""
    if len(text) <= max_width:
        return text
    return text[:max_width - len(suffix)] + suffix


def _render_list(
    rows: List[_Row],
    cursor_item_pos: int,
    item_row_indices: List[int],
    *,
    scan_path: Path,
    config_path: Optional[Path],
) -> None:
    console.clear()

    # Get terminal dimensions
    term_width = console.size.width
    viewport_size = _calculate_viewport_size()

    # Calculate visible range
    start_row, end_row = _calculate_visible_range(
        rows, cursor_item_pos, item_row_indices, viewport_size
    )

    total_items = len(item_row_indices)
    items_above = cursor_item_pos if start_row > 0 else 0
    items_below = total_items - cursor_item_pos - 1 if end_row < len(rows) - 1 else 0

    # Header
    header = Text("Symbolic Link Manager — Read-only TUI", style="bold")
    info = Text(
        f"Scan: {scan_path}  |  Config: {config_path or 'None'}  |  Items: {total_items}",
        style="dim",
    )
    help_line = Text("↑/↓ or j/k to navigate • Enter to view • q/Esc to quit", style="cyan")
    console.print(header)
    console.print(info)
    console.print(help_line)
    console.print(Rule())

    # Scroll indicator - above
    if start_row > 0:
        # Count actual items (not headers) above
        items_above_count = sum(1 for i in range(start_row) if rows[i].kind == "item")
        console.print(Text(f"  ↑ {items_above_count} more above", style="dim cyan"))

    # Calculate adaptive column widths based on terminal width
    # Formula: Name (30%), Status (10 chars fixed), Target (remaining)
    status_width = 10
    min_name_width = 12
    name_width = max(min_name_width, int(term_width * 0.3))
    target_width = max(20, term_width - name_width - status_width - 6)  # 6 for spacing/borders

    # Import box styles for table
    from rich import box

    # Render visible rows only
    # We need to handle groups: print header, then create/print table for that group's items
    current_table = None
    item_index = 0

    for row_idx in range(start_row, end_row + 1):
        if row_idx >= len(rows):
            break

        row = rows[row_idx]

        if row.kind == "header":
            # Print any existing table before starting a new group
            if current_table is not None:
                console.print(current_table)
                current_table = None

            # Print group header
            title = row.title or ""
            style = "bold magenta" if title != "unclassified" else "bold yellow"
            console.print(Text(title.upper(), style=style))

            # Create new table for this group
            current_table = Table(
                show_header=True,
                show_lines=False,
                box=box.SIMPLE,
                pad_edge=False,
                padding=(0, 1),
                collapse_padding=True,
            )
            current_table.add_column("Name", no_wrap=True, width=name_width)
            current_table.add_column("Target", no_wrap=True, width=target_width)
            current_table.add_column("Status", no_wrap=True, justify="right", width=status_width)
            continue

        assert row.item is not None

        # Create table if we somehow don't have one (shouldn't happen with proper data)
        if current_table is None:
            current_table = Table(
                show_header=True,
                show_lines=False,
                box=box.SIMPLE,
                pad_edge=False,
                padding=(0, 1),
                collapse_padding=True,
            )
            current_table.add_column("Name", no_wrap=True, width=name_width)
            current_table.add_column("Target", no_wrap=True, width=target_width)
            current_table.add_column("Status", no_wrap=True, justify="right", width=status_width)

        # Find the item position in item_row_indices to determine if selected
        selected = (row_idx == item_row_indices[cursor_item_pos])

        item = row.item
        status_text = Text("Valid", style="green") if not item.is_broken else Text("Broken", style="red")

        # Truncate name if too long
        name_display = _truncate_text(item.name, name_width)
        name_text = Text(name_display)

        # Truncate target basename if too long
        target_basename = item.target.name if item.target.name else str(item.target)
        target_display = _truncate_text(target_basename, target_width)
        target_text = Text(target_display, style="dim")

        row_style = "reverse" if selected else None
        current_table.add_row(name_text, target_text, status_text, style=row_style)
        item_index += 1

    # Print any remaining table
    if current_table is not None:
        console.print(current_table)

    # Scroll indicator - below
    if end_row < len(rows) - 1:
        items_below_count = sum(1 for i in range(end_row + 1, len(rows)) if rows[i].kind == "item")
        console.print(Text(f"  ↓ {items_below_count} more below", style="dim cyan"))


def _render_detail(item: SymlinkInfo, *, read_only: bool = True) -> None:
    console.clear()
    status = Text("Valid", style="green") if not item.is_broken else Text("Broken", style="red")

    # Build a structured, clear detail view
    body = Text()
    body.append("Name:\n", style="bold cyan")
    body.append(f"  {item.name}\n\n")

    body.append("Symlink Location:\n", style="bold cyan")
    body.append(f"  {item.path}\n\n", style="white")

    body.append("Target Path:\n", style="bold cyan")
    body.append(f"  {item.target}\n\n", style="white")

    body.append("Status: ", style="bold cyan")
    body.append(status)
    body.append("\n\n")

    if read_only:
        body.append("Modification: ", style="bold yellow")
        body.append("Disabled in MVP (Task-6 will enable).\n", style="dim")
    else:
        body.append("[Press 'e' to edit target]\n", style="dim")

    panel = Panel(
        body,
        title="[bold white]Symlink Details[/bold white]",
        subtitle="[dim]Press any key to return[/dim]",
        border_style="blue"
    )
    console.print(panel)


# ---- Public API -------------------------------------------------------------

def run_tui(scan_path: Path, config_path: Optional[Path] = None, *, max_depth: int = 20) -> int:
    """Run the interactive TUI. Returns exit code (0 normal, 1 on error)."""
    # Resolve defaults and inputs
    scan_path = Path(scan_path)
    config = load_markdown_config(config_path)

    # Scan and classify
    symlinks = scan_symlinks(scan_path=scan_path, max_depth=max_depth)
    buckets = classify_symlinks(symlinks, config, scan_root=scan_path)
    rows = _build_rows(buckets)

    # If nothing to show, print a friendly message and exit
    if _count_items(rows) == 0:
        console.clear()
        console.print(Panel(Text("No symlinks found.", style="yellow"), title="Nothing to Display"))
        return 0

    # Cursor is tracked over 'item' rows only; we keep a parallel index while rendering
    # Build a map from visual index over items to absolute row index
    item_row_indices = [idx for idx, r in enumerate(rows) if r.kind == "item"]
    cursor_item_pos = 0
    cursor_row_index = item_row_indices[cursor_item_pos]

    with _RawMode(sys.stdin.fileno()):
        while True:
            _render_list(
                rows,
                cursor_item_pos,
                item_row_indices,
                scan_path=scan_path,
                config_path=config_path
            )
            key = _read_key()
            if key in ("q", "Q", "ESC"):
                break
            if key in ("UP", "k"):
                cursor_item_pos = max(0, cursor_item_pos - 1)
            elif key in ("DOWN", "j"):
                cursor_item_pos = min(len(item_row_indices) - 1, cursor_item_pos + 1)
            elif key == "ENTER":
                # Show detail view for the selected item
                sel_abs_row = item_row_indices[cursor_item_pos]
                sel = rows[sel_abs_row]
                if sel.kind == "item" and sel.item is not None:
                    _render_detail(sel.item, read_only=True)
                    # Wait for a single key to return
                    _read_key()
            # Recompute absolute row index (not used except for details)
            cursor_row_index = item_row_indices[cursor_item_pos]

    console.clear()
    return 0

