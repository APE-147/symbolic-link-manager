Symlink Manager (MVP)
=====================

Safe symlink scanner, classifier, and migrator for macOS/Linux.

Status: MVP scaffolding only. Core features will be added in subsequent tasks.

Quick Start
-----------

1. Create a virtualenv (or use `pipx`).
2. Install in editable mode: `pip install -e .[dev]`
3. Check CLI is wired: `link --version`.

Goals
-----
- Read-only symlink discovery
- Rich TUI for triage
- Safe migration with backups and rollback

Tech Stack
---------
- Python 3.9+
- click (CLI)
- rich (terminal UI)
- pytest, ruff (dev tools)

