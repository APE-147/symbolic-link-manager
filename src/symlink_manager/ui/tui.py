from __future__ import annotations

"""Interactive TUI (Task-4) using Rich for rendering.

Capabilities (read-only for MVP):
- Display symlinks grouped by project (classified first; "unclassified" last)
- Show name, current target, and status (green OK, red BROKEN)
- Keyboard navigation: Up/Down (or k/j), Enter to view details, q/Esc to quit
- Integrates with scanner + classifier modules

Notes:
- Input handling uses raw terminal mode (termios) to keep dependencies minimal
- Rendering uses Rich Console and Tables; full-screen re-render per keypress
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

def _render_list(
    rows: List[_Row],
    cursor: int,
    *,
    scan_path: Path,
    config_path: Optional[Path],
) -> None:
    console.clear()
    header = Text("Symbolic Link Manager — Read-only TUI", style="bold")
    info = Text(
        f"Scan: {scan_path}  |  Config: {config_path or 'None'}  |  Items: {_count_items(rows)}",
        style="dim",
    )
    help_line = Text("↑/↓ or j/k to navigate • Enter to view • q/Esc to quit", style="cyan")
    console.print(header)
    console.print(info)
    console.print(help_line)
    console.print(Rule())

    # Render per-group tables; highlight the selected row if it belongs here
    i = 0
    for row in rows:
        if row.kind == "header":
            title = row.title or ""
            style = "bold magenta" if title != "unclassified" else "bold yellow"
            console.print(Text(title.upper(), style=style))
            continue
        assert row.item is not None
        selected = (i == cursor)

        # We render one-row table per item for simple per-row highlighting
        tbl = Table(show_edge=False, show_header=False, pad_edge=False)
        tbl.add_column("Name", no_wrap=True)
        tbl.add_column("Target", overflow="fold")
        tbl.add_column("Status", no_wrap=True, justify="right")

        item = row.item
        status_text = Text("OK", style="green") if not item.is_broken else Text("BROKEN", style="red")
        name_text = Text(item.name)
        target_text = Text(str(item.target), style="dim")

        row_style = "reverse" if selected else None
        tbl.add_row(name_text, target_text, status_text, style=row_style)
        console.print(tbl)
        i += 1


def _render_detail(item: SymlinkInfo, *, read_only: bool = True) -> None:
    console.clear()
    status = Text("OK", style="green") if not item.is_broken else Text("BROKEN", style="red")
    body = Text()
    body.append(f"Name: {item.name}\n")
    body.append(f"Link: {item.path}\n")
    body.append(f"Target: {item.target}\n")
    body.append("Status: ")
    body.append(status)
    body.append("\n\n")

    if read_only:
        body.append("Modification: ", style="bold")
        body.append("Disabled in MVP (Task-6 will enable).\n", style="yellow")
    else:
        body.append("Press 'e' to edit target.\n")

    panel = Panel(body, title="Symlink Details", subtitle="Press any key to return")
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
            _render_list(rows, cursor_item_pos, scan_path=scan_path, config_path=config_path)
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

