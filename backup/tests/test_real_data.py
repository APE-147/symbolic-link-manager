#!/usr/bin/env python3
"""Test the actual TUI rendering with real data to debug misalignment."""

from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich import box

# Import the actual TUI code
import sys
sys.path.insert(0, "src")

from symlink_manager.core.scanner import scan_symlinks
from symlink_manager.core.classifier import classify_symlinks, load_markdown_config

# Scan the actual user data
scan_path = Path("/Users/niceday/Developer/Cloud/Dropbox/-Code-/Scripts")
config = load_markdown_config(None)

symlinks = scan_symlinks(scan_path=scan_path, max_depth=20)
buckets = classify_symlinks(symlinks, config, scan_root=scan_path)

print(f"Found {len(symlinks)} symlinks in {len(buckets)} groups")

# Simulate the rendering logic for the first few items
console = Console()
term_width = console.size.width

# Calculate column widths (from lines 265-270)
status_width = 10
min_name_width = 12
name_width = max(min_name_width, int(term_width * 0.3))
target_width = max(20, term_width - name_width - status_width - 6)

print(f"Terminal width: {term_width}")
print(f"Column widths: Name={name_width}, Target={target_width}, Status={status_width}")
print()

# Render first group (unclassified)
if "unclassified" in buckets:
    items = buckets["unclassified"][:5]  # First 5 items

    # Print header
    console.print(Text("UNCLASSIFIED", style="bold yellow"))

    # Create table (from lines 298-309)
    table = Table(
        show_header=True,
        show_lines=False,
        box=box.SIMPLE,
        pad_edge=False,
        padding=(0, 1),
        collapse_padding=True,
        width=term_width - 2
    )
    table.add_column("Name", no_wrap=True, width=name_width)
    table.add_column("Target", no_wrap=True, width=target_width)
    table.add_column("Status", no_wrap=True, justify="right", width=status_width)

    # Add rows (from lines 332-345)
    for item in items:
        status_text = Text("Valid", style="green") if not item.is_broken else Text("Broken", style="red")
        name_text = Text(item.name)
        target_basename = item.target.name if item.target.name else str(item.target)
        target_text = Text(target_basename, style="dim")

        table.add_row(name_text, target_text, status_text)

    console.print(table)

print("\n" + "="*80)
print("DEBUG: If you see misalignment above, the issue is REAL.")
print("If the table looks perfect, the issue might be specific to raw mode or scrolling.")
print("="*80)
