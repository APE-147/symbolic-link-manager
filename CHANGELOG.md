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

### Fixed
- **BREAKING CHANGE**: Renamed CLI command from `link` to `lk` to avoid conflict with Unix system's built-in `/bin/link` command
- Updated default config path from `~/.config/link/` to `~/.config/lk/`

