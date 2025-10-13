# AGENTS.md - Symbolic Link Manager Project

## Header / Project Snapshot

* **Feature Slug**: symlink-manager-mvp
* **Cycle**: 1
* **Owner**: Claude Code (codex-feature agent)
* **Env**: macOS (Darwin 24.6.0)
* **Progress**: 55.56% (from docs/TASKS.md - 5/9 tasks completed)
* **Branch**: feat/symlink-manager-mvp (to be created)
* **Savepoint Tag**: savepoint/2025-10-13-symlink-manager-mvp (to be created)
* **FF Status**: Not applicable (CLI tool, no runtime feature flags needed)
* **Kill Switch**: Not applicable (local CLI tool)
* **Links**:
  - `docs/REQUIRES.md` - User requirements & application scenarios
  - `docs/PLAN.md` - Decision questions & cycle progress
  - `docs/TASKS.md` - Task checklist with acceptance criteria
  - `docs/FEATURE_SPEC.md` - Feature specification (to be created)
  - `docs/blast-radius.md` - Impact analysis (to be created)
  - `docs/stack-fingerprint.md` - Tech stack & tooling (to be created)

## Definitions

### FWU (Feature Work Unit)
A minimal end-to-end increment completable in ≤1 day with acceptance criteria and verification method.

### BRM (Blast Radius Map)
List of affected modules, interfaces, data structures, and deployment surfaces with dependency relationships.

For this project:
- **Scope**: Local CLI tool, no external APIs or services
- **Affected Areas**: User's filesystem at `/Users/niceday/Developer/Cloud/Dropbox/-Code-`
- **Risk Level**: HIGH - involves file/directory migration operations
- **Mitigation**: Mandatory backups, atomic operations, dry-run mode, rollback capability

### Invariants & Contracts
Constraints that must hold after modifications:

1. **No data loss**: All file migrations must preserve content integrity
2. **Atomic operations**: Link updates and file moves are transactional (succeed together or fail together)
3. **Backup guarantee**: Every migration creates timestamped backup before execution
4. **Idempotency**: Running same operation twice produces same result
5. **Read-only scanning**: Link discovery never modifies filesystem
6. **Permission preservation**: Migrated files/dirs retain original permissions

### Touch Budget (Allowed Modification Scope)
Files/directories this project is allowed to create/modify:

**Allowed:**
- `src/symlink_manager/**/*.py` - All source code
- `docs/**/*.md` - Documentation
- `tests/**/*.py` - Test files
- `data/` - Runtime data (backups, logs, config)
- `pyproject.toml`, `README.md`, `CHANGELOG.md`, `.gitignore`

**Restricted (user confirmation required):**
- User's target scan directory: `/Users/niceday/Developer/Cloud/Dropbox/-Code-`
- Migration source/destination paths (only during explicit user-initiated migration)

**Forbidden:**
- System directories (`/usr`, `/etc`, `/System`, etc.)
- User home directory root (except within specified scan path)

### FF (Feature Flag) Convention
Not applicable for this CLI tool - no runtime flags needed. All functionality available after installation.

## Top TODO (≤1h granularity)

All TODOs mirror `docs/TASKS.md` top-level items.

1. **[ ] Task-1: Establish project baseline & documentation**
   - Acceptance: Project structure follows Python src-layout; all docs files (REQUIRES/PLAN/TASKS/AGENTS) exist and valid
   - Verification: `ls -la`, `ls -la docs/`, `ls -la src/` show expected structure

2. **[ ] Task-2: Implement symlink scanner module**
   - Acceptance: Recursive scan finds all symlinks; handles permission errors; returns structured data
   - Verification: `python -m symlink_manager.core.scanner --scan-path <test-dir>` outputs JSON

3. **[ ] Task-3: Implement Markdown classification system**
   - Acceptance: Parse Markdown config; classify links; separate classified/unclassified
   - Verification: `python -m symlink_manager.core.classifier --config <test-config>` outputs categories

4. **[ ] Task-4: Implement interactive TUI**
   - Acceptance: Display classified (top) and unclassified (bottom) links; keyboard navigation works
   - Verification: `lk` command launches TUI; arrow keys navigate; Enter selects

5. **[ ] Task-5: Implement target path view & modification**
   - Acceptance: Show current target; accept new target input; validate before migration
   - Verification: Select link in TUI → shows target → input new path → validation feedback

6. **[ ] Task-6: Implement safe migration & backup**
   - Acceptance: Create backup before migration; atomic move; rollback on failure; log all operations
   - Verification: `python -m symlink_manager.services.migrator --dry-run` shows plan; actual run creates backup

7. **[ ] Task-7: Implement global CLI installation**
   - Acceptance: `pip install -e .` installs; `lk` command globally available
   - Verification: `lk --version`, `lk --help` work from any directory

8. **[ ] Task-8: Implement test suite & quality gates**
   - Acceptance: Unit + integration tests; ≥80% coverage; all tests pass
   - Verification: `pytest tests/ -v --cov=src/symlink_manager` shows ≥80% coverage, all green

## Run Log (reverse chronological)

### 2025-10-13 19:15 - Critical Fix: Renamed CLI command from `link` to `lk` (Blocker resolved)
- **Issue**: Command name `link` conflicted with Unix system's built-in `/bin/link` command (for creating hard links)
- **Impact**: Users could not launch the tool - running `link` invoked system command instead of our CLI
- **Solution**: Renamed CLI command to `lk` to avoid conflict
- **Changes made**:
  - Updated `pyproject.toml`: `[project.scripts]` entry point from `link` to `lk`
  - Updated `cli.py`: changed prog_name from "link" to "lk" and config path from `~/.config/link/` to `~/.config/lk/`
  - Updated all documentation: REQUIRES.md, TASKS.md, FEATURE_SPEC.md, AGENTS.md, README.md
  - Updated all examples and acceptance criteria
- **Verification**:
  - `pip install -e .` completed successfully
  - `lk --version` outputs: "symlink-manager, version 0.1.0"
  - `lk --help` displays correct usage information
  - `which lk` confirms command at: `/Users/niceday/Developer/Python/miniconda/envs/System/bin/lk`
  - Unix `link` command still at `/bin/link` (no conflict)
- **Status**: Blocker resolved, tool now fully accessible via `lk` command

### 2025-10-13 18:20 - Interactive TUI (Task-4)
- Added `src/symlink_manager/ui/tui.py` using Rich for rendering and a raw terminal key handler for navigation.
- Features: grouped list (classified first, `unclassified` last), color-coded status (green OK, red BROKEN), arrow/j/k navigation, Enter opens read-only detail view, q/Esc to quit.
- Integrated with scanner + classifier; reads config from `--config` or `~/.config/lk/projects.md` fallback.
- Wired CLI default command to launch TUI: `lk [--target PATH] [--config FILE]` (group options on root command). Keeps operations read-only.
- Next: implement editable target input + validation (Task-5) and safe migration (Task-6).

### 2025-10-13 17:45 - Markdown classification system (Task-3)
- Implemented `src/symlink_manager/core/classifier.py` with Markdown parser (sections `## Project` + `- pattern`), glob matching, first-match-wins, and graceful fallback to all `unclassified` on missing/invalid config.
- Added CLI: `python -m symlink_manager.core.classifier --config <path> --scan-path <dir>` printing JSON buckets (includes `unclassified`).
- Patterns match against absolute, relative-to-scan-root, and basename variants of the symlink path (not the target).
- Added unit tests `tests/test_classifier.py` covering parsing, relative matching, first-match-wins, and fallback behavior. All tests pass (`pytest -q` → 7 passed).
- Next: wire buckets into TUI grouping view.

### 2025-10-13 17:10 - Symlink scanner module (Task-2)
- Implemented `src/symlink_manager/core/scanner.py` with recursive scan (default `max_depth=20`), circular/broken detection, and graceful permission handling.
- Added `SymlinkInfo` dataclass (path, name, target, is_broken, project) and JSON CLI: `python -m symlink_manager.core.scanner --scan-path <dir>`.
- Integrated `rich` progress spinner for scan feedback.
- Added unit tests `tests/test_scanner.py` covering normal, broken, circular, and permission-error scenarios.
- Next: wire into TUI + classifier.

### 2025-10-13 16:34 - Project scaffolding (src-layout)
- Added `pyproject.toml` (Python ≥3.9; deps: click, rich; dev: pytest, ruff; console script `lk`).
- Created package skeleton `src/symlink_manager/` with `cli.py`, `core/`, `services/`, `utils/` and `__init__` files.
- Added `README.md` and `CHANGELOG.md` placeholders.
- Next: wire scanner/classifier stubs to CLIs, add tests and data dirs.

### 2025-10-13 00:00 - Cycle 1 initialized
- Created docs baseline: REQUIRES.md (user requirements), PLAN.md (Cycle 1 with 8 decision questions), TASKS.md (8 top-level tasks)
- Created AGENTS.md with project snapshot and definitions
- Selected PLAN options: All A (focus on safety, simplicity, and quality)
- Next: Initialize Git repo, create savepoint, scaffold project structure

## Replan

**Blockers**: None currently

**Decisions Pending**:
1. TUI library choice: rich vs prompt_toolkit (lean toward rich for simpler API)
2. Backup retention policy: keep all vs time-based cleanup (suggest configurable with sane default)

**Next Actions**:
1. Initialize Git repository and create savepoint tag
2. Generate FEATURE_SPEC.md with detailed requirements and acceptance criteria
3. Create BRM (blast-radius.md) for filesystem impact analysis
4. Detect tech stack and create stack-fingerprint.md
5. Scaffold Python project structure (src-layout)

## BRM / Touch Budget / Invariants Summary

**Blast Radius**:
- **Modules**: New project, no existing modules affected
- **Data**: User's symlinks at scan path + migration targets (high-risk operations)
- **Deployment**: Local Python package installation

**Touch Budget Status**: Within bounds (all changes in project directory)

**Invariants Status**: Defined and documented above

## Evidence Index

*No test reports or artifacts yet - will be populated as tasks complete*

**Test Reports**: (pending)
**Audit Reports**: (pending)
**Performance Baselines**: (pending)
**Screenshots**: (pending)
**Build Artifacts**: (pending)
