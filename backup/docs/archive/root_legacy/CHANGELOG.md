# Changelog

All notable changes to this project will be documented in this file.

Format based on Keep a Changelog; versions follow SemVer.

## [0.1.0] - 2025-10-13
### Added
- Initial project scaffolding (src-layout)
- `pyproject.toml` with dependencies (click, rich) and dev tools (pytest, ruff)
- Package skeleton: `symlink_manager` with `core/`, `services/`, `utils/`
- Symlink scanner with recursive discovery, broken link detection, and circular link handling
- Markdown-based classification system with glob pattern matching
- Interactive TUI with keyboard navigation and rich formatting
- CLI entry point wired to `lk` command
- **TUI Scrolling**: Viewport-based rendering for large lists (100+ symlinks)
  - Only renders visible items for O(viewport_size) performance
  - Scroll indicators: "↑ N more above" / "↓ N more below"
  - Centered cursor with smooth navigation
  - Group headers preserved during scrolling
- **Adaptive Column Widths**: Dynamic sizing based on terminal width (80-200 cols)
  - Name column: 30% of terminal width (min 12 chars)
  - Status column: Fixed 10 chars
  - Target column: Remaining space (min 20 chars)
  - Text truncation with "…" suffix for long names/paths
- Test script for generating 60+ test symlinks (`tests/create_test_symlinks.sh`)
- Comprehensive documentation: `docs/TUI_SCROLLING.md`
 - Target editing (Task-5): In-TUI edit flow with validation-only (no migration yet)
   - Minimal raw-mode line editor (press `e` on list)
   - Validation result panel in detail view
 - Validator service: `services.validator.validate_target_change`
   - Absolute path requirement; parent existence & writability checks
   - No-op detection (same as current target)
   - System directory guards; destination-exists conflict detection
   - Outside scan-root warning for user awareness

### Fixed
- **BREAKING CHANGE**: Renamed CLI command from `link` to `lk` to avoid conflict with Unix system's built-in `/bin/link` command
- Updated default config path from `~/.config/link/` to `~/.config/lk/`
- TUI now handles large lists without overflow (previously items became invisible)
- **CRITICAL FIX**: TUI table alignment - Fixed severe misalignment bug causing diagonal/zigzag display pattern
  - Root cause: Each row was creating its own Table object with independent borders/padding
  - Solution: Create single Table per group, add all rows to that table, then print once
  - Result: Perfect column alignment across all rows in each group
  - Added regression tests: `tests/test_tui_alignment.py` (2 tests verifying single table per group)
  - Added visual alignment tests using captured console output: `tests/test_tui_alignment_visual.py`
  - Switched table box style to `box.SQUARE` to ensure visible vertical separators in exported text

### Tests
- New validator unit tests: `tests/test_validator.py` (6 passing)
- All tests green: `20 passed`
