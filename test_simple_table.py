#!/usr/bin/env python3
"""Simple test to verify Rich table alignment"""

from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

# Test 1: Simple table without width constraints
print("=== Test 1: Basic table ===")
table1 = Table(show_header=True, box=box.SIMPLE, padding=(0, 1))
table1.add_column("Name", no_wrap=True)
table1.add_column("Target", no_wrap=True)
table1.add_column("Status", no_wrap=True, justify="right")

table1.add_row("data", "rss-inbox-data", "Valid")
table1.add_row("python3", "python3.9", "Broken")
table1.add_row("python", "python3.9", "Broken")

console.print(table1)
print()

# Test 2: Table with fixed widths
print("=== Test 2: Fixed width columns ===")
table2 = Table(
    show_header=True,
    box=box.SIMPLE,
    padding=(0, 1),
    collapse_padding=True,
    pad_edge=False
)
table2.add_column("Name", no_wrap=True, width=20)
table2.add_column("Target", no_wrap=True, width=30)
table2.add_column("Status", no_wrap=True, justify="right", width=10)

table2.add_row("data", "rss-inbox-data", "Valid")
table2.add_row("python3", "python3.9", "Broken")
table2.add_row("python", "python3.9", "Broken")

console.print(table2)
print()

# Test 3: Multiple groups (simulating the actual issue)
print("=== Test 3: Multiple groups (current approach) ===")

console.print("[bold yellow]UNCLASSIFIED[/]")
table3a = Table(
    show_header=True,
    box=box.SIMPLE,
    pad_edge=False,
    padding=(0, 1),
    collapse_padding=True,
)
table3a.add_column("Name", no_wrap=True, width=20)
table3a.add_column("Target", no_wrap=True, width=30)
table3a.add_column("Status", no_wrap=True, justify="right", width=10)

table3a.add_row("data", "rss-inbox-data", "Valid")
table3a.add_row("python3", "python3.9", "Broken")

console.print(table3a)
print()

console.print("[bold magenta]PROJECT-A[/]")
table3b = Table(
    show_header=True,
    box=box.SIMPLE,
    pad_edge=False,
    padding=(0, 1),
    collapse_padding=True,
)
table3b.add_column("Name", no_wrap=True, width=20)
table3b.add_column("Target", no_wrap=True, width=30)
table3b.add_column("Status", no_wrap=True, justify="right", width=10)

table3b.add_row("alpha-link", "alpha-target", "Valid")
table3b.add_row("beta-link", "beta-target", "Broken")

console.print(table3b)
