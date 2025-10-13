#!/usr/bin/env python3
"""Test if group headers cause misalignment with tables."""

from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich import box

console = Console()

# Test: Multiple groups with headers
print("\n=== Test: Multiple groups with headers (current pattern) ===")

for group_name in ["PROJECT-A", "PROJECT-B", "UNCLASSIFIED"]:
    # Print group header (line 295)
    style = "bold magenta" if group_name != "UNCLASSIFIED" else "bold yellow"
    console.print(Text(group_name, style=style))

    # Create and print table
    term_width = console.size.width
    name_width = 24
    target_width = 40
    status_width = 10

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

    # Add some rows
    for i in range(3):
        table.add_row(
            Text(f"link_{i}"),
            Text(f"target_{i}", style="dim"),
            Text("Valid", style="green")
        )

    console.print(table)
    console.print()  # Blank line

print("="*80)
print("If the above shows misalignment, the issue is in group header + table interaction.")
print("="*80)
