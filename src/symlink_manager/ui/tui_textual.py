"""
Textual-based TUI for Symbolic Link Manager

This module provides a complete multi-screen Textual implementation that solves
the terminal rendering issues present in the simple-term-menu implementation.

Key improvements:
- Virtual DOM with smart diffing (eliminates flickering)
- Three-screen architecture (MainList → Detail → Edit)
- Hierarchical Tree widget for 3-level classification
- Built-in keyboard navigation (j/k, arrows, Enter, Esc)
- Real-time input validation in edit mode
- Alternate screen buffer (automatic, no manual clearing needed)

Usage (via CLI):
  lk --ui-engine textual --target /path/to/scan [--config ...]

Architecture:
  LKApp (App)
  ├── MainListScreen (primary view with HierarchicalTree)
  ├── DetailScreen (shows symlink info + action buttons)
  └── EditScreen (target path editing with validation)

References:
  - Research Report: docs/TEXTUAL_RESEARCH_REPORT.md
  - Textual Docs: https://textual.textualize.io/
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

try:  # pragma: no cover - exercised by Textual Pilot tests
    from textual.app import App, ComposeResult
    from textual.containers import Container, Horizontal
    from textual.screen import Screen
    from textual.widgets import (
        Header,
        Footer,
        Tree,
        Static,
        Input,
        Button,
    )
    from textual.binding import Binding
    from textual import on
except Exception as _e:  # pragma: no cover
    # Defer import errors until runtime so default installs remain usable
    _TEXTUAL_IMPORT_ERROR = _e
    App = object  # type: ignore
    ComposeResult = object  # type: ignore
    Screen = object  # type: ignore
    Container = Horizontal = object  # type: ignore
    Header = Footer = Tree = Static = Input = Button = object  # type: ignore
    Binding = on = object  # type: ignore
else:
    _TEXTUAL_IMPORT_ERROR = None

# Import project modules (always safe, even if Textual not installed)
from ..core.scanner import SymlinkInfo, scan_symlinks
from ..core.classifier import classify_symlinks_auto_hierarchy, load_markdown_config
from ..services.validator import validate_target_change


# ============================================================================
#  Widget: HierarchicalTree
# ============================================================================

class HierarchicalTree(Tree):  # type: ignore[misc]
    """Three-level hierarchical tree for symlink display.

    Structure:
        [PRIMARY] Desktop
          [SECONDARY] Projects
            ✓ MyApp → /target/path
            ✗ BrokenLink → /missing
          [SECONDARY] Archive
        [PRIMARY] Service

    Data format:
        Dict[primary_name, Dict[secondary_name, List[SymlinkInfo]]]
    """

    def load_data(self, hierarchical: Dict[str, Dict[str, List[SymlinkInfo]]]) -> None:
        """Load hierarchical symlink data into the tree.

        Args:
            hierarchical: Dict[primary, Dict[secondary, List[SymlinkInfo]]]
        """
        self.clear()
        root = self.root
        root.expand()

        for primary, secondaries in hierarchical.items():
            primary_node = root.add(
                f"[bold blue][PRIMARY][/] {primary}",
                data={"type": "primary", "name": primary},
                expand=True
            )

            for secondary, symlinks in secondaries.items():
                secondary_node = primary_node.add(
                    f"[bold green][SECONDARY][/] {secondary}",
                    data={"type": "secondary", "name": secondary},
                    expand=True
                )

                for symlink in symlinks:
                    project = symlink.project_name or "unknown"
                    target = symlink.target
                    status_icon = "✓" if not symlink.is_broken else "✗"
                    color = "cyan" if not symlink.is_broken else "red"

                    secondary_node.add_leaf(
                        f"[{color}]{status_icon} {project}[/] → {target}",
                        data={"type": "symlink", "info": symlink}
                    )


# ============================================================================
#  Screen: DetailScreen
# ============================================================================

class DetailScreen(Screen):  # type: ignore[misc]
    """Detail view showing complete symlink information.

    Displays:
    - Path, Target, Primary, Secondary, Project name
    - Status (Valid/Broken)
    - Action buttons (Edit, Back)

    Keybindings:
    - Escape/q: Return to main list
    - e: Open edit screen
    """

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("e", "edit", "Edit"),
    ]

    def __init__(self, symlink_info: SymlinkInfo):
        super().__init__()
        self.info = symlink_info

    CSS = """
    DetailScreen {
        align: center middle;
    }
    #detail-box {
        width: 80%;
        height: auto;
        border: solid blue;
        padding: 1 2;
    }
    .detail-label {
        color: $text-muted;
    }
    .detail-value {
        color: $text;
        margin-bottom: 1;
    }
    """

    def compose(self) -> ComposeResult:  # type: ignore[override]
        yield Header()
        with Container(id="detail-box"):
            yield Static("[bold]Symlink Details[/]")
            yield Static("Path:", classes="detail-label")
            yield Static(str(self.info.path), classes="detail-value")
            yield Static("Target:", classes="detail-label")
            yield Static(str(self.info.target), classes="detail-value")
            yield Static("Primary:", classes="detail-label")
            yield Static(self.info.primary_category or "N/A", classes="detail-value")
            yield Static("Secondary:", classes="detail-label")
            yield Static(self.info.secondary_category or "N/A", classes="detail-value")
            yield Static("Project:", classes="detail-label")
            yield Static(self.info.project_name or "N/A", classes="detail-value")
            yield Static("Status:", classes="detail-label")

            status_color = "green" if not self.info.is_broken else "red"
            status_text = "Valid" if not self.info.is_broken else "BROKEN"
            yield Static(f"[{status_color}]{status_text}[/]", classes="detail-value")

            with Horizontal():
                yield Button("Edit (e)", id="edit-btn", variant="primary")
                yield Button("Back (Esc)", id="back-btn")
        yield Footer()

    def action_back(self) -> None:
        self.app.pop_screen()  # type: ignore[attr-defined]

    def action_edit(self) -> None:
        self.app.push_screen(EditScreen(self.info))  # type: ignore[attr-defined]

    @on(Button.Pressed, "#edit-btn")  # type: ignore[misc]
    def on_edit_pressed(self) -> None:
        self.action_edit()

    @on(Button.Pressed, "#back-btn")  # type: ignore[misc]
    def on_back_pressed(self) -> None:
        self.action_back()


# ============================================================================
#  Screen: EditScreen
# ============================================================================

class EditScreen(Screen):  # type: ignore[misc]
    """Edit view for changing symlink target path.

    Features:
    - Input field pre-filled with current target
    - Real-time validation with color-coded feedback
    - Save/Cancel buttons

    Keybindings:
    - Escape: Cancel and return

    Note: Actual save operation is TODO (placeholder notification)
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, symlink_info: SymlinkInfo):
        super().__init__()
        self.info = symlink_info

    CSS = """
    EditScreen {
        align: center middle;
    }
    #edit-box {
        width: 80%;
        height: auto;
        border: solid green;
        padding: 1 2;
    }
    #validation-msg {
        height: 2;
    }
    """

    def compose(self) -> ComposeResult:  # type: ignore[override]
        yield Header()
        with Container(id="edit-box"):
            yield Static("[bold]Edit Target Path[/]")
            yield Static(f"Current: {self.info.target}")
            yield Input(
                value=str(self.info.target),
                placeholder="Enter new target path",
                id="target-input"
            )
            yield Static("", id="validation-msg")

            with Horizontal():
                yield Button("Save", id="save-btn", variant="success")
                yield Button("Cancel (Esc)", id="cancel-btn")
        yield Footer()

    def action_cancel(self) -> None:
        self.app.pop_screen()  # type: ignore[attr-defined]

    @on(Input.Changed, "#target-input")  # type: ignore[misc]
    def on_input_changed(self, event: Input.Changed) -> None:  # type: ignore[name-defined]
        """Real-time validation as user types."""
        msg = self.query_one("#validation-msg", Static)
        path = Path(event.value)

        if not event.value:
            msg.update("[yellow]⚠ Path cannot be empty[/]")
        elif not path.is_absolute():
            msg.update("[yellow]⚠ Path must be absolute[/]")
        elif path.exists():
            msg.update("[green]✓ Valid path[/]")
        else:
            msg.update("[red]✗ Path does not exist[/]")

    @on(Button.Pressed, "#save-btn")  # type: ignore[misc]
    def on_save(self) -> None:
        new_target = self.query_one("#target-input", Input).value
        # TODO: Integrate with services.update_symlink(self.info.path, new_target)
        self.notify(f"TODO: Save {new_target}")  # type: ignore[attr-defined]
        self.app.pop_screen()  # type: ignore[attr-defined]

    @on(Button.Pressed, "#cancel-btn")  # type: ignore[misc]
    def on_cancel(self) -> None:
        self.action_cancel()


# ============================================================================
#  Screen: MainListScreen
# ============================================================================

class MainListScreen(Screen):  # type: ignore[misc]
    """Primary screen showing hierarchical symlink list.

    Features:
    - Three-level tree (Primary → Secondary → Symlinks)
    - Keyboard navigation (j/k, arrows)
    - Enter to view details
    - Search placeholder (/)

    Keybindings:
    - q: Quit app
    - j/down: Move down
    - k/up: Move up
    - /: Search (placeholder)
    - Enter: Open detail view
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("/", "search", "Search"),
        Binding("j", "move_down", "Down"),
        Binding("k", "move_up", "Up"),
    ]

    def __init__(self, hierarchical_data: Dict[str, Dict[str, List[SymlinkInfo]]]):
        super().__init__()
        self.hierarchical_data = hierarchical_data

    CSS = """
    MainListScreen {
        layout: vertical;
    }
    #tree-container {
        height: 100%;
        border: solid blue;
    }
    """

    def compose(self) -> ComposeResult:  # type: ignore[override]
        yield Header()
        with Container(id="tree-container"):
            yield HierarchicalTree("Symbolic Links", id="symlink-tree")
        yield Footer()

    def on_mount(self) -> None:  # type: ignore[override]
        """Load data and focus tree after screen mounts."""
        tree = self.query_one(HierarchicalTree)
        tree.load_data(self.hierarchical_data)
        tree.focus()

    @on(Tree.NodeSelected)  # type: ignore[misc]
    def on_tree_selected(self, event: Tree.NodeSelected) -> None:  # type: ignore[name-defined]
        """Handle node selection - open detail view if symlink selected."""
        node_data = event.node.data
        if node_data and node_data.get("type") == "symlink":
            symlink_info = node_data["info"]
            self.app.push_screen(DetailScreen(symlink_info))  # type: ignore[attr-defined]

    def action_quit(self) -> None:
        self.app.exit()  # type: ignore[attr-defined]

    def action_search(self) -> None:
        # TODO: Implement search screen/modal
        self.notify("Search not implemented yet")  # type: ignore[attr-defined]

    def action_move_down(self) -> None:
        tree = self.query_one(HierarchicalTree)
        tree.action_cursor_down()

    def action_move_up(self) -> None:
        tree = self.query_one(HierarchicalTree)
        tree.action_cursor_up()


# ============================================================================
#  App: LKApp
# ============================================================================

class LKApp(App):  # type: ignore[misc]
    """Symbolic Link Manager - Textual TUI Application.

    Entry point for the Textual-based interface. Manages screen stack and
    global app state.

    Args:
        hierarchical_data: Pre-classified symlink data
            Dict[primary, Dict[secondary, List[SymlinkInfo]]]
    """

    CSS = """
    Screen {
        background: $surface;
    }
    """

    def __init__(self, hierarchical_data: Dict[str, Dict[str, List[SymlinkInfo]]], **kwargs: Any):
        super().__init__(**kwargs)
        self.hierarchical_data = hierarchical_data

    def on_mount(self) -> None:  # type: ignore[override]
        """Push main screen on app startup."""
        self.push_screen(MainListScreen(self.hierarchical_data))


# ============================================================================
#  Public API
# ============================================================================

def run_textual_ui(
    scan_path: Path,
    config_path: Optional[Path] = None,
    *,
    max_depth: int = 20,
    filter_rules: Optional[object] = None,
) -> int:
    """Run Textual TUI. Returns exit code (0 = success, 1 = error).

    This is the main entry point called from CLI with --ui-engine textual.

    Args:
        scan_path: Root directory to scan for symlinks
        config_path: Path to Markdown classification config (or None)
        max_depth: Maximum scan depth (default 20)
        filter_rules: FilterRules object for symlink filtering (or None)

    Returns:
        Exit code: 0 for normal exit, 1 for errors

    Raises:
        RuntimeError: If textual is not installed
    """
    # Check Textual availability
    if _TEXTUAL_IMPORT_ERROR is not None:  # pragma: no cover
        raise RuntimeError(
            "Textual UI requested but 'textual' is not installed.\n"
            "Install with: pip install -e .[textual]"
        ) from _TEXTUAL_IMPORT_ERROR

    # Prepare filter parameters for scanner
    exclude_patterns = None
    directories_only = True
    filter_garbled = True
    filter_hash_targets = True

    if filter_rules is not None:
        from ..core.filter_config import FilterRules
        if isinstance(filter_rules, FilterRules):
            exclude_patterns = filter_rules.exclude_patterns
            directories_only = filter_rules.directories_only
            filter_garbled = filter_rules.filter_garbled
            filter_hash_targets = filter_rules.filter_hash_targets

    # Scan symlinks
    symlinks = scan_symlinks(
        scan_path=scan_path,
        max_depth=max_depth,
        exclude_patterns=exclude_patterns,
        directories_only=directories_only,
        filter_garbled=filter_garbled,
        filter_hash_targets=filter_hash_targets,
    )

    # Classify into 3-level hierarchy
    config = load_markdown_config(config_path)
    hierarchical_buckets = classify_symlinks_auto_hierarchy(
        symlinks, config, scan_root=scan_path
    )

    # Handle empty results
    if not hierarchical_buckets:
        print("No symlinks found.")
        return 0

    # Launch Textual app
    app = LKApp(hierarchical_buckets)
    app.run()
    return 0


__all__ = [
    "LKApp",
    "MainListScreen",
    "DetailScreen",
    "EditScreen",
    "HierarchicalTree",
    "run_textual_ui",
]
