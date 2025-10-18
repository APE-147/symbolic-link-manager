# Feature Spec: Fix TUI Display Issues

## Problem Statement

The TUI (Text User Interface) for the symlink manager (`lk` command) suffers from display issues that degrade user experience:

1. **Screen flickering/jittering** during navigation
2. **Excessive downward scrolling** polluting terminal scrollback
3. **Header residue** remaining at top after navigation

These issues make the tool frustrating to use and fail to meet user expectations for smooth TUI navigation (like vim, less, htop).

## Background

The TUI uses the `simple-term-menu` library for menu navigation and `rich` for styled output. The current implementation:
- Calls `console.clear()` multiple times
- Uses `clear_screen=True` in TerminalMenu, causing full screen clears on every redraw
- Does not use alternate screen buffer
- Outputs to main terminal scrollback buffer

## Goals

1. **Eliminate screen flickering** - Navigation should be smooth and stable
2. **Prevent scrollback pollution** - TUI should not leave output in terminal history
3. **Remove header residue** - Clean transitions with no artifacts
4. **Maintain all functionality** - No regression in features or test coverage
5. **Improve terminal compatibility** - Work on various terminal sizes

## Non-Goals

- Adding new features to the TUI
- Changing the menu structure or navigation keys
- Modifying core logic (scanner, classifier, validator)
- Supporting non-ANSI terminals

## Constraints

- Must maintain backward compatibility with existing CLI interface
- All 31 existing tests must pass
- Changes limited to `src/symlink_manager/ui/tui.py` only
- Cannot introduce new dependencies

## Solution Design

### 1. Alternate Screen Buffer
Use Rich's `console.screen()` context manager to:
- Isolate TUI display from terminal scrollback
- Provide clean full-screen canvas
- Automatically restore original screen on exit

### 2. Optimized Screen Clearing
- Set `clear_screen=False` in all TerminalMenu instances
- Set `clear_menu_on_exit=False` to prevent clear on menu exit
- Keep strategic `console.clear()` calls only in detail/edit views for clean transitions

### 3. Terminal Size Detection
- Add `_get_terminal_size()` utility function
- Disable preview pane on terminals < 100 columns wide
- Calculate safe menu height to prevent overflow

### 4. Menu Height Limiting
- Add `menu_entries_max_height` parameter to TerminalMenu
- Calculate based on terminal height minus UI chrome (title, status bar, preview, margins)

### 5. Cursor Management
- Handled automatically by `console.screen()` context manager
- Cursor hidden during TUI operation, restored on exit

## Data/Interface Changes

No changes to:
- `run_tui()` function signature
- Menu navigation keys (↑/↓/Enter/q//)
- Scanner, classifier, or validator interfaces
- Test interfaces

New internal utility:
```python
def _get_terminal_size() -> tuple[int, int]:
    """Get terminal size safely. Returns (columns, rows)."""
```

## Acceptance Criteria

### Positive Cases
1. Running `lk --target <path>` shows stable menu with no flickering
2. Navigating with ↑/↓ produces smooth cursor movement
3. Quitting with `q` leaves terminal scrollback unchanged
4. Pressing Enter to view details shows clean transition
5. Search with `/` filters list smoothly
6. Terminal is fully restored on exit (cursor visible, scrollback intact)
7. Works on small (80×24) and large (200×60) terminals
8. All 31 tests pass

### Negative Cases
1. Does not leave artifacts or residue on screen
2. Does not pollute terminal scrollback buffer
3. Does not crash or freeze on rapid key presses
4. Does not fail on unsupported terminal sizes (graceful degradation)

## Risk Assessment

**Technical Risks:**
- **Low**: Changes isolated to single file (tui.py)
- **Low**: Using Rich's built-in context manager (well-tested)
- **Low**: All changes backward-compatible

**UX Risks:**
- **Low**: May behave differently on non-standard terminals (minimal risk given target macOS/Linux)

**Performance Risks:**
- **None**: No performance impact expected

## Observability

### Metrics
- User-reported flickering issues (should drop to zero)
- Test suite pass rate (must remain 100%)

### Logs
- No additional logging needed
- Errors in alternate screen management would be visible as Python exceptions

### Monitoring
- Manual testing per docs/TESTING.md checklist
- Automated: `pytest -q` confirms no regressions

## Rollback Strategy

Since this is not deployed software but a development tool:
- **Immediate**: `git revert <commit>` if issues found
- **No FF needed**: This is a bugfix, not a feature flag-able change
- **Testing**: Manual testing on actual Terminal.app before considering complete

## Security & Privacy

**No security or privacy implications:**
- No data collection
- No network communication
- No credential handling
- No new file I/O (reads existing symlinks only)

## Accessibility

**Improvements:**
- Cleaner display benefits users with visual sensitivity
- Stable screen reduces cognitive load
- Alternate screen buffer standard practice (familiar to screen reader users)

**No negative impact:**
- All keyboard navigation unchanged
- Color schemes unchanged
- Text content unchanged

## Internationalization

Not applicable - TUI displays file paths and system information only.

## Dependencies

**Existing (no changes):**
- `rich` - already used for console output
- `simple-term-menu` - already used for menu navigation
- `click` - already used for CLI prompts

**New:**
- `shutil` (stdlib) - for terminal size detection
- `sys` (stdlib) - already imported

## Implementation Checklist

- [x] Add terminal size detection utility
- [x] Wrap run_tui() in console.screen() context
- [x] Set clear_screen=False in main menu
- [x] Set clear_menu_on_exit=False in all menus
- [x] Add adaptive preview_size based on terminal width
- [x] Add menu_entries_max_height parameter
- [x] Run full test suite (31 tests must pass)
- [x] Create docs/TESTING.md with manual test cases
- [ ] Perform manual testing per TESTING.md
- [ ] Update AGENTS.md with results
- [ ] Update TASKS.md with completion status

## Success Metrics

**Before:**
- Screen flickers during navigation
- Menu scrolls down excessively
- Header residue remains at top

**After:**
- ✅ Zero flickering during navigation
- ✅ No scrollback pollution
- ✅ No header residue
- ✅ All 31 tests pass
- ✅ Clean exit with terminal restored

## Future Enhancements (Out of Scope)

- Colorblind-friendly color schemes
- Configurable key bindings
- Mouse support
- Split-screen diff view for symlink changes
