# Blast Radius Map (BRM)

## Overview
This document maps the impact scope of the Symbolic Link Manager project to ensure all modifications stay within safe boundaries.

## Affected Modules

### New Modules (Created by this project)
- `src/symbolic_link_changer/` - All Python modules (new codebase)
  - `cli.py` - Entry point
  - `core/scanner.py` - Symlink discovery
  - `core/modifier.py` - Symlink modification
  - `services/classifier.py` - Classification logic
  - `utils/paths.py` - Path utilities

### External Dependencies
- `click` - CLI framework (stable, well-tested)
- `rich` - Terminal UI (stable, no breaking changes expected)
- Standard library only: `pathlib`, `os`, `shutil`, `logging`

## Data Impact

### Read-Only Operations
- **Symlink Scanning**: Reads directory structure at `/Users/niceday/Developer/Cloud/Dropbox/-Code-`
  - **Risk Level**: LOW
  - **Mitigation**: No filesystem modifications, only read operations
  - **Failure Mode**: Permission errors handled gracefully

- **Configuration Reading**: Reads classification config file (if provided)
  - **Risk Level**: LOW
  - **Mitigation**: Fallback to unclassified mode if config missing/invalid

### Write Operations (High Risk)

#### 1. Symlink Modification
- **Affected**: User's symbolic links in scan directory
- **Risk Level**: HIGH
- **Operations**:
  - Read current symlink target
  - Unlink existing symlink
  - Create new symlink with new target
- **Mitigation**:
  - Backup original target before modification
  - Atomic operation (fail together or succeed together)
  - User confirmation required
  - Rollback on failure
  - Dry-run mode available

#### 2. Backup Creation
- **Affected**: `data/backups/<timestamp>/`
- **Risk Level**: LOW
- **Operations**: Copy original target to backup location
- **Mitigation**:
  - Timestamped directories prevent conflicts
  - No deletion of backups (manual cleanup only)
  - Clear error messages if backup fails (abort modification)

#### 3. Logging
- **Affected**: `data/logs/symlink_changer.log`
- **Risk Level**: VERY LOW
- **Operations**: Append log entries
- **Mitigation**: Rotating log handler, no sensitive data logged

## Deployment Impact

### Installation
- **Scope**: User's Python environment (via pipx)
- **Risk Level**: LOW
- **Changes**:
  - Installs `symbolic_link_changer` package
  - Registers global `link` command
  - Creates isolated virtualenv (pipx)
- **Mitigation**: Uses standard Python packaging, uninstallable via `pipx uninstall`

### Filesystem Layout
- **Project Root**: `/Users/niceday/Developer/Cloud/Dropbox/-Code-/Scripts/system/data-storage/symbolic_link_changer/`
  - Risk: None (project-local)
- **User Data**: `data/backups/`, `data/logs/`
  - Risk: Grows over time (cleanup command needed)
- **Config**: `~/.config/link/projects.md` (optional)
  - Risk: None (user-created)

## Interface Impact

### CLI Interface
- **New Command**: `link`
- **Risk Level**: LOW
- **Collision Risk**: Minimal (short common name, but namespaced to symlink management)
- **Mitigation**: Clear help text, version info, uninstallable

### APIs (Internal)
All interfaces are internal to the package. No external APIs exposed.

## Dependency Relationships

```
User's Filesystem
    ↓ (reads)
Scanner Module
    ↓ (data)
Classifier Module
    ↓ (displays)
TUI (Rich)
    ↓ (user input)
Modifier Module
    ↓ (writes, backed up)
User's Symlinks + data/backups/
```

## Risk Matrix

| Component | Operation | Risk Level | Mitigation | Rollback Strategy |
|-----------|-----------|------------|------------|-------------------|
| Scanner | Read symlinks | LOW | Graceful error handling | N/A (read-only) |
| Classifier | Parse config | LOW | Fallback to unclassified | N/A (read-only) |
| TUI | Display + navigate | VERY LOW | Input validation | N/A (no persistence) |
| Modifier | Update symlink | HIGH | Backup + confirmation + atomic ops | Restore from backup |
| Backup | Copy target | MEDIUM | Pre-check disk space, clear errors | Manual cleanup if failed |
| Logger | Write logs | VERY LOW | Rotating handler | N/A (logs only) |

## Invariants to Maintain

1. **No data loss**: Every modification creates backup first
2. **Atomicity**: Symlink updates succeed fully or fail fully (no partial state)
3. **Read-only default**: Scanning never modifies filesystem
4. **Explicit confirmation**: Modifications require user consent
5. **Idempotency**: Re-running same operation produces same result
6. **Permission respect**: Never escalate privileges, fail safely on permission errors

## Out of Scope (Not Affected)

- **System directories**: `/usr`, `/etc`, `/System`, `/Applications`
- **Other users' files**: Only operates on current user's files
- **Network resources**: Local filesystem only
- **Hard links**: Only symbolic links managed
- **Link creation/deletion**: Only retargeting existing symlinks

## Touch Budget Validation

### Allowed File Operations
✅ Read any symlink in scan path
✅ Read classification config file
✅ Write to `data/backups/`
✅ Write to `data/logs/`
✅ Modify symlinks in scan path (with confirmation)
✅ Create/modify project files in `src/`, `docs/`, `tests/`

### Forbidden Operations
❌ Modify system directories
❌ Escalate privileges
❌ Delete files (only retarget symlinks)
❌ Modify other users' files
❌ Network operations

## Monitoring & Observability

- **Operation Logs**: All modifications logged to `data/logs/symlink_changer.log`
- **Backup Trail**: Every modification creates backup entry in `data/backups/<timestamp>/`
- **User Feedback**: Rich terminal output shows all operations in real-time
- **Dry-run Mode**: Test without side effects (`--dry-run`)

## Rollback Procedures

### Emergency Rollback (Git-level)
```bash
git checkout savepoint/2025-10-13-symlink-manager-mvp
```

### User-level Rollback (Symlink modification)
1. Navigate to `data/backups/`
2. Find backup with desired timestamp
3. Manually restore original target:
   ```bash
   ln -sf $(cat data/backups/<timestamp>/original_target.txt) /path/to/symlink
   ```

### Uninstall
```bash
pipx uninstall symbolic_link_changer
# Manual cleanup if needed:
rm -rf ~/.config/link/
rm -rf /path/to/project/data/
```

