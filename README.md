Symlink Manager (MVP)
=====================

Safe symlink scanner, classifier, and migrator for macOS/Linux.

Status: MVP scaffolding only. Core features will be added in subsequent tasks.

Quick Start
-----------

1. Create a virtualenv (or use `pipx`).
2. Install in editable mode: `pip install -e .[dev]`
3. Check CLI is wired: `lk --version`.
4. Launch TUI: `lk`
   - Arrow keys (or j/k) navigate
   - Press `/` to search/filter items
   - Preview pane auto-shows symlink details
   - Enter shows full details with action menu
   - `e` edits target (validation only)

Goals
-----
- Read-only symlink discovery
- Rich TUI for triage
- Edit target path with pre-migration validation (Task-5)
- Safe migration with backups and rollback

Tech Stack
---------
- Python 3.9+
- click (CLI)
- rich (terminal UI rendering)
- simple-term-menu (interactive navigation)
- pytest, ruff (dev tools)

Editing a Target (Validation Only)
----------------------------------
- In the list view, select a symlink and press `e`.
- Enter a new absolute destination path for the real file/directory.
- The app runs safety checks (absolute path, parent exists and is writable, no-op detection, system path guards, destination conflict checks) and displays errors/warnings.
- This does not change any files; migration and backup are covered in Task-6.
