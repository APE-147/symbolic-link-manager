from __future__ import annotations

"""Interactive TUI using simple-term-menu for navigation.

Refactored from custom termios/tty implementation to use the well-tested
simple-term-menu library, reducing code complexity by ~200 lines.

Key improvements:
- Built-in search functionality (press '/' to search)
- Preview pane showing symlink details
- Cleaner, more maintainable code
- Better cross-platform compatibility
- Library-managed scrolling and navigation

Capabilities (read-only for MVP):
- Display symlinks grouped by project (classified first; "unclassified" last)
- Show name, current target, and status (green Valid, red BROKEN)
- Keyboard navigation: Up/Down, Enter to view details, q/Esc to quit
- Search: Press '/' to filter items
- Preview pane: Auto-shows symlink info
- Integrates with scanner + classifier modules
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import shutil
import sys
import click

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from simple_term_menu import TerminalMenu

from ..core.scanner import SymlinkInfo, scan_symlinks
from ..core.classifier import (
    classify_symlinks,
    classify_symlinks_auto_hierarchy,
    load_markdown_config,
)
from ..services.validator import validate_target_change, ValidationResult


console = Console()


# ---- Terminal utility functions ---------------------------------------------

def _get_terminal_size() -> tuple[int, int]:
    """Get terminal size safely. Returns (columns, rows)."""
    try:
        cols, rows = shutil.get_terminal_size()
        return cols, rows
    except Exception:
        return 80, 24  # Fallback to standard size


# ---- View model -------------------------------------------------------------

@dataclass
class _Row:
    kind: str  # 'primary_header' | 'secondary_header' | 'item'
    title: Optional[str] = None
    project: Optional[str] = None
    item: Optional[SymlinkInfo] = None
    indent_level: int = 0  # 0 for primary, 1 for secondary, 2 for items


def _build_rows(buckets: Dict[str, List[SymlinkInfo]]) -> List[_Row]:
    """Flatten buckets into a list of rows with headers before each group.

    Ensures 'unclassified' group appears at the end.
    """
    rows: list[_Row] = []
    keys: List[str] = list(k for k in buckets.keys() if k != "unclassified")
    if "unclassified" in buckets:
        keys.append("unclassified")

    for proj in keys:
        rows.append(_Row(kind="primary_header", title=proj, indent_level=0))
        for item in buckets.get(proj, []):
            rows.append(_Row(kind="item", project=proj, item=item, indent_level=1))
    return rows


def _build_rows_hierarchical(hierarchical_buckets: Dict[str, Dict[str, List[SymlinkInfo]]]) -> List[_Row]:
    """Flatten 3-level hierarchical buckets into rows with proper indentation.

    Format:
        [PRIMARY]
          [Secondary]
            ✓ project → target

    Args:
        hierarchical_buckets: Dict[primary, Dict[secondary, List[SymlinkInfo]]]

    Returns:
        List of _Row objects with indent_level set
    """
    rows: list[_Row] = []

    # Ensure unclassified appears last
    primary_keys = [k for k in hierarchical_buckets.keys() if k != "unclassified"]
    if "unclassified" in hierarchical_buckets:
        primary_keys.append("unclassified")

    for primary in primary_keys:
        # Add primary header (Level 1)
        rows.append(_Row(kind="primary_header", title=primary, indent_level=0))

        secondary_buckets = hierarchical_buckets[primary]
        for secondary in sorted(secondary_buckets.keys()):
            # Add secondary header (Level 2)
            rows.append(_Row(kind="secondary_header", title=secondary, indent_level=1))

            # Add items (Level 3)
            for item in secondary_buckets[secondary]:
                rows.append(_Row(kind="item", project=primary, item=item, indent_level=2))

    return rows


def _count_items(rows: List[_Row]) -> int:
    return sum(1 for r in rows if r.kind == "item")


# ---- Preview and detail rendering -------------------------------------------

def _generate_preview(item: Optional[SymlinkInfo]) -> str:
    """Generate preview text for simple-term-menu preview pane."""
    if item is None:
        return ""

    lines = []
    lines.append(f"Name: {item.name}")
    lines.append(f"Location: {item.path}")
    lines.append(f"Target: {item.target}")
    status = "Valid" if not item.is_broken else "BROKEN"
    lines.append(f"Status: {status}")
    lines.append("")
    lines.append("Press Enter for details and actions")

    return "\n".join(lines)


def _render_header(scan_path: Path, total_items: int, is_filtered: bool) -> None:
    """Render a single-line header above the menu to avoid title duplication."""
    filter_label = " (filtered)" if is_filtered else ""
    header = Text(
        f"Symbolic Link Manager | Scan: {scan_path} | Items: {total_items}{filter_label}",
        style="bold",
    )
    console.print(header)


def _render_detail(item: SymlinkInfo, *, read_only: bool = True, proposed: Optional[Path] = None, validation: Optional[ValidationResult] = None) -> None:
    """Show detailed symlink information in a Rich Panel."""
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

    if proposed is not None:
        body.append("Proposed Target:\n", style="bold cyan")
        body.append(f"  {proposed}\n\n", style="white")

    body.append("Status: ", style="bold cyan")
    body.append(status)
    body.append("\n\n")

    if validation is not None:
        if validation.ok:
            body.append("Validation: ", style="bold green")
            body.append("OK\n", style="green")
        else:
            body.append("Validation: ", style="bold red")
            body.append("FAILED\n", style="red")

        if validation.errors:
            body.append("Errors:\n", style="bold red")
            for e in validation.errors:
                body.append(f"  - {e}\n", style="red")
        if validation.warnings:
            body.append("Warnings:\n", style="bold yellow")
            for w in validation.warnings:
                body.append(f"  - {w}\n", style="yellow")

        body.append("\n", style="white")

    if read_only:
        body.append("Hint: Choose 'Edit Target' to modify.\n", style="dim")

    panel = Panel(
        body,
        title="[bold white]Symlink Details[/bold white]",
        subtitle="[dim]Press Enter to continue[/dim]",
        border_style="blue"
    )
    console.print(panel)


def _show_detail_menu(item: SymlinkInfo, scan_path: Path) -> str:
    """Show detail view with action options. Returns action: 'back', 'edit', 'quit'."""
    _render_detail(item, read_only=True)

    # Action menu
    action_menu = TerminalMenu(
        ["← Back to List", "Edit Target", "Quit"],
        title="Actions",
        menu_cursor="→ ",
        menu_cursor_style=("fg_cyan", "bold"),
        menu_highlight_style=("bg_cyan", "fg_black"),
        clear_screen=False,
        clear_menu_on_exit=False,
    )

    choice = action_menu.show()
    if choice == 0:
        return "back"
    elif choice == 1:
        return "edit"
    elif choice == 2:
        return "quit"
    else:
        return "back"


def _handle_edit(item: SymlinkInfo, scan_path: Path):
    """Handle editing target path using click.prompt()."""
    console.clear()
    console.print(f"[bold]Edit target for:[/] {item.name}")
    console.print(f"[dim]Current:[/] {item.target}")
    console.print()

    try:
        new_target = click.prompt(
            "New target path",
            default=str(item.target),
            show_default=True,
        )

        new_path = Path(new_target)
        vr = validate_target_change(item, new_path, scan_root=scan_path)

        # Show validation results
        if vr.ok:
            console.print("[green]✓ Validation passed[/]")
        else:
            console.print("[red]✗ Validation failed[/]")
            for error in vr.errors:
                console.print(f"  [red]• {error}[/]")

        if vr.warnings:
            for warning in vr.warnings:
                console.print(f"  [yellow]⚠ {warning}[/]")

        console.print()
        console.print("[dim]Press Enter to continue[/]")
        input()

    except click.Abort:
        console.print("[yellow]Edit cancelled[/]")
        console.print("[dim]Press Enter to continue[/]")
        input()


# ---- Public API -------------------------------------------------------------

def run_tui(
    scan_path: Path,
    config_path: Optional[Path] = None,
    *,
    max_depth: int = 20,
    filter_rules: Optional[object] = None,
) -> int:
    """Run the interactive TUI using simple-term-menu. Returns exit code (0 normal, 1 on error).

    Args:
        scan_path: Root directory to scan for symlinks
        config_path: Path to Markdown classification config
        max_depth: Maximum directory depth to scan
        filter_rules: FilterRules object for symlink filtering, or None to disable
    """
    # Resolve defaults and inputs
    scan_path = Path(scan_path)
    config = load_markdown_config(config_path)

    # Prepare filter parameters for scanner
    exclude_patterns = None
    directories_only = True
    filter_garbled = True
    filter_hash_targets = True
    is_filtered = False
    if filter_rules is not None:
        from ..core.filter_config import FilterRules
        if isinstance(filter_rules, FilterRules):
            exclude_patterns = filter_rules.exclude_patterns
            directories_only = filter_rules.directories_only
            filter_garbled = filter_rules.filter_garbled
            filter_hash_targets = filter_rules.filter_hash_targets
            is_filtered = bool(exclude_patterns) or directories_only or filter_garbled or filter_hash_targets

    # Scan and classify
    symlinks = scan_symlinks(
        scan_path=scan_path,
        max_depth=max_depth,
        exclude_patterns=exclude_patterns,
        directories_only=directories_only,
        filter_garbled=filter_garbled,
        filter_hash_targets=filter_hash_targets,
    )

    # Use hierarchical classification with auto-detection
    hierarchical_buckets = classify_symlinks_auto_hierarchy(symlinks, config, scan_root=scan_path)
    rows = _build_rows_hierarchical(hierarchical_buckets)

    # If nothing to show, print a friendly message and exit
    if _count_items(rows) == 0:
        console.clear()
        console.print(Panel(Text("No symlinks found.", style="yellow"), title="Nothing to Display"))
        return 0

    # Use alternate screen buffer to prevent scrollback pollution and flickering
    with console.screen():
        # Detect terminal size for adaptive behavior
        cols, rows_count = _get_terminal_size()
        preview_size = 0.3 if cols >= 100 else 0  # Disable preview on narrow terminals

        # Build menu entries with hierarchical indentation
        menu_items = []
        item_to_symlink = {}  # Map menu index to SymlinkInfo

        for idx, row in enumerate(rows):
            # Calculate indentation (2 spaces per level)
            indent = "  " * row.indent_level

            if row.kind == "primary_header":
                # Primary category header (Level 1)
                title = row.title or "unknown"
                menu_items.append(f"{indent}[{title.upper()}]")
                item_to_symlink[len(menu_items) - 1] = None

            elif row.kind == "secondary_header":
                # Secondary category header (Level 2)
                title = row.title or "unknown"
                menu_items.append(f"{indent}[{title}]")
                item_to_symlink[len(menu_items) - 1] = None

            elif row.kind == "item":
                # Symlink item (Level 3)
                item = row.item
                status = "✓" if not item.is_broken else "✗"
                target_name = item.target.name if item.target and item.target.name else str(item.target)
                # Show project_name from hierarchy instead of just item.name
                project_name = item.project_name or item.name
                display = f"{indent}{status} {project_name} → {target_name}"
                menu_items.append(display)
                item_to_symlink[len(menu_items) - 1] = item

        # Create menu with optimized settings to prevent flickering
        total_items = _count_items(rows)
        menu = TerminalMenu(
            menu_items,
            menu_cursor="→ ",
            menu_cursor_style=("fg_cyan", "bold"),
            menu_highlight_style=("bg_cyan", "fg_black"),
            cycle_cursor=True,
            clear_screen=False,  # Don't clear screen - we're in alternate buffer
            clear_menu_on_exit=False,  # Don't clear on exit
            preview_command=lambda idx: _generate_preview(item_to_symlink.get(idx)),
            preview_size=preview_size,
            skip_empty_entries=True,  # Skip headers when navigating
            status_bar=f"↑/↓ Navigate | Enter Details | / Search | q Quit",
            status_bar_style=("fg_cyan",),
            search_key="/",  # Press / to search
        )

        # Render header once before entering menu loop
        console.clear()
        _render_header(scan_path, total_items, is_filtered)

        # Main loop
        while True:
            selected_idx = menu.show()

            # User quit (Esc or q)
            if selected_idx is None:
                break

            # Get selected item
            selected_item = item_to_symlink.get(selected_idx)
            if selected_item is None:
                continue  # Header selected (shouldn't happen with skip_empty_entries), ignore

            # Handle actions
            action = _show_detail_menu(selected_item, scan_path)
            if action == "quit":
                break
            elif action == "edit":
                _handle_edit(selected_item, scan_path)

            # Re-render header after returning from detail/edit views
            console.clear()
            _render_header(scan_path, total_items, is_filtered)

    # Alternate screen buffer automatically restored by context manager
    return 0
