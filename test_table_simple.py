#!/usr/bin/env python3
"""Minimal test case to isolate TUI alignment issue."""

from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

# Test 1: Simple table with basic settings (similar to current code)
print("\n=== Test 1: Simple table (current code style) ===")
table1 = Table(
    show_header=True,
    show_lines=False,
    box=box.SIMPLE,
    pad_edge=False,
    padding=(0, 1),
    collapse_padding=True,
)
table1.add_column("Name", no_wrap=True, width=20)
table1.add_column("Target", no_wrap=True, width=30)
table1.add_column("Status", no_wrap=True, width=10)

table1.add_row("data", "rss-inbox-data", "Valid")
table1.add_row("python3", "python3.9", "Broken")
table1.add_row("python", "python3.9", "Broken")

console.print(table1)

# Test 2: Multiple individual tables (like the OLD buggy code would do)
print("\n=== Test 2: Creating one table per row (OLD buggy pattern) ===")
for name, target, status in [("data", "rss-inbox-data", "Valid"), ("python3", "python3.9", "Broken"), ("python", "python3.9", "Broken")]:
    single_row_table = Table(
        show_header=False,
        show_lines=False,
        box=None,
        pad_edge=False,
        padding=(0, 1),
    )
    single_row_table.add_column("Name", no_wrap=True, width=20)
    single_row_table.add_column("Target", no_wrap=True, width=30)
    single_row_table.add_column("Status", no_wrap=True, width=10)
    single_row_table.add_row(name, target, status)
    console.print(single_row_table)

# Test 3: Verify terminal width
print(f"\n=== Test 3: Console info ===")
print(f"Terminal width: {console.size.width}")
print(f"Terminal height: {console.size.height}")
