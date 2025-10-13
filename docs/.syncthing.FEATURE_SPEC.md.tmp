# Feature Specification: Symbolic Link Changer

## Problem Background

Users with large codebases often create symbolic links to reference files/directories across projects. Over time:
- Symlinks multiply and become difficult to track
- Original targets may move, causing broken links
- No centralized way to audit or update symlinks
- Manual updates are error-prone and time-consuming

**Target User**: Individual developers managing personal codebase in `/Users/niceday/Developer/Cloud/Dropbox/-Code-/`

## Goals

1. **Discovery**: Automatically find all symbolic links in target directory
2. **Organization**: Classify symlinks by project for easier navigation
3. **Inspection**: View current symlink targets interactively
4. **Maintenance**: Update symlink targets safely with backup/rollback
5. **Accessibility**: Provide global CLI command `lk` for easy access

## Non-Goals

1. Managing hard links (only symbolic links)
2. Team collaboration / multi-user configuration sync
3. Automatic symlink creation or deletion
4. Cross-platform GUI (TUI only)
5. Remote filesystem or network symlinks
6. Symlink validation or target existence checking (informational only)

## Constraints

- **Safety First**: Never modify symlinks without explicit user confirmation
- **Reversibility**: All modifications must be backed up and recoverable
- **Read-Only Scan**: Default operation is non-destructive
- **Local Only**: Operates on local filesystem only
- **Single User**: No authentication or authorization needed

## Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Data loss from incorrect symlink modification | High | Backup before modify + confirmation prompt + rollback on failure |
| Permission errors in target directory | Medium | Graceful error handling with clear messages |
| Infinite recursion from circular symlinks | Medium | Track visited paths, set max depth limit |
| Performance issues with very large directories | Low | Progress indicator, async scanning (future) |
| Classification config parsing errors | Low | Validate config format, provide clear error messages |

## Data & Interface Changes

### Data Model

**Symlink Entity**:
```python
@dataclass
class SymlinkInfo:
    path: Path           # Full path to symlink
    name: str            # Symlink name (basename)
    target: Path         # Current target (resolved)
    is_broken: bool      # Whether target exists
    project: str | None  # Classification (None if unclassified)
```

**Classification Config** (Markdown format):
```markdown
# Project Classification

## ProjectName1
- pattern/glob/here/*
- another/pattern/**/*.py

## ProjectName2
- different/path/*
```

### Interfaces

**CLI Commands**:
```bash
# Interactive mode (default)
lk

# Specify target directory
lk --target /path/to/directory

# Specify classification config
lk --config /path/to/config.md

# Dry-run mode (no modifications)
lk --dry-run

# Version info
lk --version

# Help
lk --help
```

**Interactive TUI Flow**:
1. Launch TUI with classified symlinks list
2. Arrow keys to navigate
3. Enter on symlink → show details panel:
   - Current target path
   - Broken status
   - Modification interface
4. Input new target → confirmation prompt
5. Accept → backup + modify + verify
6. Reject → return to list
7. Quit (q/Esc) → exit gracefully

## Acceptance Criteria (with Negative Cases)

### 1. Symlink Discovery
**Positive**:
- Given a directory with nested symlinks, when scan runs, then all symlinks are found
- Given a directory with broken symlinks, when scan runs, then they are identified as broken

**Negative**:
- Given a directory without read permissions, when scan runs, then error is reported clearly
- Given a circular symlink, when scan runs, then it doesn't cause infinite loop

### 2. Classification
**Positive**:
- Given a valid config with glob patterns, when classification runs, then symlinks match correctly
- Given symlinks matching multiple patterns, when classification runs, then first match wins

**Negative**:
- Given an invalid config file, when parsing runs, then clear error message is shown
- Given a missing config file, when requested, then fallback to "all unclassified" mode

### 3. Interactive Navigation
**Positive**:
- Given a TUI with symlinks, when user presses arrow keys, then selection moves correctly
- Given a selected symlink, when user presses Enter, then target is displayed

**Negative**:
- Given a TUI with no symlinks found, when displayed, then shows "no symlinks found" message
- Given invalid key input, when pressed, then is ignored (no crash)

### 4. Modification Safety
**Positive**:
- Given a symlink modification request, when user confirms, then backup is created first
- Given a successful modification, when completed, then new target is verified
- Given a failed modification, when detected, then rollback restores original

**Negative**:
- Given a modification without confirmation, when attempted, then is blocked
- Given a backup failure, when detected, then modification is aborted
- Given insufficient permissions, when modifying, then clear error is shown

### 5. Global Command
**Positive**:
- Given pipx installation, when `lk` is run, then command is found in PATH
- Given `lk --version`, when run, then version is displayed

**Negative**:
- Given missing dependencies, when `lk` runs, then helpful error message is shown

## Observability

### Logging
- **Location**: `data/logs/symlink_changer.log`
- **Levels**: DEBUG, INFO, WARNING, ERROR
- **Content**:
  - Scan operations (start, count, duration)
  - Modifications (before/after targets, user confirmation, backup path)
  - Errors (permissions, invalid paths, failures)

### Metrics (Future)
- Number of symlinks discovered
- Classification distribution
- Modification success/failure rate
- Scan duration

### User Feedback
- Progress indicators during scan
- Rich-formatted tables for symlink lists
- Color-coded status (green=valid, red=broken)
- Clear confirmation prompts with before/after comparison

## Feature Flag & Rollback Strategy

**Not applicable** for CLI tool (not a service).

**Safety mechanisms**:
- `--dry-run` flag for safe testing
- Explicit confirmation required for modifications
- Automatic backup before changes
- Manual rollback: restore from `data/backups/`

## Privacy & Security

### Privacy
- No data transmitted externally
- No telemetry or analytics
- All operations local to user's machine

### Security
- **Input Validation**:
  - Sanitize all file paths (prevent path traversal)
  - Validate target paths exist and are accessible
  - Reject suspicious patterns (e.g., `/dev/`, `/sys/`)
- **Permissions**:
  - Respect filesystem permissions
  - Never escalate privileges
  - Fail safely when permission denied
- **Secrets**:
  - No credentials or API keys required
  - No `.env` file needed (all config in project settings or CLI args)

### Dependencies
- Regular audits: `pip-audit` or `safety check`
- Pinned versions in `pyproject.toml`
- Minimal dependency footprint (click, rich only)

## Implementation Phases

### Phase 1: MVP (Target: Day 1-2)
- [x] Project scaffolding
- [ ] Basic symlink scanner
- [ ] Simple classification (config parsing)
- [ ] Interactive TUI (read-only)
- [ ] Global `lk` command

### Phase 2: Safety & Modification (Target: Day 3-4)
- [ ] Modification logic with backup
- [ ] Confirmation prompts
- [ ] Rollback capability
- [ ] Error handling & validation

### Phase 3: Polish & Testing (Target: Day 5)
- [ ] Comprehensive tests (≥80% coverage)
- [ ] Documentation (README, examples)
- [ ] Quality gates (ruff, mypy)
- [ ] Performance optimization

## Scenarios (Gherkin-style)

### Scenario 1: First-time User Discovers Symlinks
```gherkin
Given I have never used the tool before
When I run `lk` for the first time
Then I see a welcome message
And a list of all symlinks in the default directory
And they are grouped by "unclassified"
```

### Scenario 2: User Creates Classification Config
```gherkin
Given I want to organize symlinks by project
When I create ~/.config/lk/projects.md with project patterns
And run `lk --config ~/.config/lk/projects.md`
Then symlinks are grouped by project name
And unclassified symlinks appear at the bottom
```

### Scenario 3: User Updates Symlink Target
```gherkin
Given I have a symlink pointing to an old location
When I select the symlink and press Enter in lk
And input a new target path
And confirm the change
Then the symlink is backed up
And the target is updated
And I see a success message with the new target
```

### Scenario 4: User Accidentally Confirms Wrong Target
```gherkin
Given I updated a symlink to the wrong target
When I check data/backups/ directory
Then I find the backup file with timestamp
And I can manually restore the original target
```

### Scenario 5: Tool Handles Broken Symlink
```gherkin
Given I have a symlink pointing to a non-existent target
When I run `lk`
Then the symlink appears with a "BROKEN" indicator
And I can select it to update to a valid target
```

### Scenario 6: Dry-run Mode Prevents Modifications
```gherkin
Given I want to test without making changes
When I run `lk --dry-run`
Then I can navigate and view symlinks
But modification actions are disabled
And a banner shows "DRY-RUN MODE"
```

## Open Questions

1. **Config file location**: Should it be:
   - `~/.config/lk/projects.md` (XDG standard)
   - `~/.lk-projects.md` (home directory)
   - User-specified only via `--config`?

   **Decision**: Support all three (priority: --config > ~/.config/lk/projects.md > fallback to unclassified)

2. **Backup retention**: How long to keep backups?
   - Keep all backups (manual cleanup)
   - Auto-delete after N days
   - Limit to last N backups per symlink

   **Decision**: Keep all, provide `lk --clean-backups` command (future)

3. **Max recursion depth**: Should we limit scan depth?
   **Decision**: Set default max_depth=20, make configurable via `--max-depth`

4. **Broken symlink handling**: Should we offer to delete broken symlinks?
   **Decision**: No auto-delete; only allow retargeting (user can manually delete)
