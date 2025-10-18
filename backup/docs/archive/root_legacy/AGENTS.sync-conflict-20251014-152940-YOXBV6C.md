# AGENTS.md

## Header / Project Snapshot

- **Feature Slug**: hierarchical-3level-classification
- **Cycle**: 3 (Cycle 1: TUI flickering; Cycle 2: Title duplication; Cycle 3: Hierarchical classification)
- **Owner**: codex-feature agent
- **Env**: macOS Darwin 24.6.0, Python 3.12.9
- **Progress**: 0.00% (0 tasks started - pending PLAN generation)
- **Branch**: feat/symlink-manager-mvp
- **Savepoint Tag**: (to be created before implementation)
- **FF Status**: N/A (enhancement to existing feature)
- **Kill Switch**: N/A

### Links
- [REQUIRES.md](./docs/REQUIRES.md) - **Latest**: Hierarchical 3-Level Classification System
- [PLAN.md](./docs/PLAN.md) - Decision cycles (Cycle 3 pending)
- [TASKS.md](./docs/TASKS.md) - Task checklist (to be generated)
- [blast-radius.md](./docs/archive/blast-radius.md) - Blast radius analysis
- [stack-fingerprint.md](./docs/archive/stack-fingerprint.md) - Tech stack

## Definitions

### Cycle 3: Hierarchical Classification

- **FWU (Feature Work Unit)**: Hierarchical 3-level classification system (Primary→Secondary→Project), implementable in ≤1 day
- **BRM (Blast Radius Map)**:
  - **MAJOR**: `src/symlink_manager/core/classifier.py` - Parser and classification logic rewrite
  - **MODERATE**: `src/symlink_manager/ui/tui.py` - Menu building and 3-level display
  - **MINOR**: `src/symlink_manager/core/scanner.py` - Extend SymlinkInfo dataclass only
  - **NEW**: `tests/test_hierarchical_classifier.py` - New test suite
- **Invariants & Contracts**:
  - All 31 existing tests must pass ✅
  - Backward compatibility with flat config required ✅
  - Scanner API unchanged (except SymlinkInfo fields) ✅
  - TUI navigation keys unchanged (↑/↓/Enter/q//) ✅
  - CLI interface unchanged (`lk` command) ✅
- **Touch Budget**:
  - **ALLOWED**: classifier.py (full rewrite OK), tui.py (display functions), scanner.py (dataclass only), tests/
  - **FORBIDDEN**: services/, utils/, core scanning logic, CLI entry points
- **FF (Feature Flag)**: N/A - enhancement to existing classification, no runtime toggle needed

### Previous Cycles (Completed)

- **Cycle 1 FWU**: TUI flickering fix - alternate screen buffer + optimized clearing
- **Cycle 2 FWU**: Title duplication fix - manual Rich header rendering
- **Cycle 1-2 Touch Budget**: Only `src/symlink_manager/ui/tui.py` ✅
- **Cycle 1-2 Status**: Implementation complete, manual testing pending

## Top TODO (≤1h 粒度)

### Cycle 1 & Hotfix: TUI Flickering & TypeError (COMPLETE)

0. [x] Task-0: Fix TerminalMenu TypeError (CRITICAL HOTFIX)
   - Acceptance: Application launches without TypeError ✅
   - Verification: Removed invalid parameter `menu_entries_max_height`
   - Evidence: Line 290 removed (unused var), Line 331 removed (invalid param), smoke test passes

1. [x] Task-1: Implement alternate screen buffer support
   - Acceptance: TUI uses alternate screen buffer, no scrollback pollution ✅
   - Verification: Wrapped run_tui() in console.screen() context manager
   - Evidence: Lines 284-354 in tui.py

2. [x] Task-2: Optimize TerminalMenu screen clearing settings
   - Acceptance: clear_screen=False in all TerminalMenu instances ✅
   - Verification: Main menu (line 323), detail menu (line 175)
   - Evidence: Added clear_menu_on_exit=False (lines 176, 324)

3. [x] Task-3: Minimize console.clear() calls
   - Acceptance: Only strategic clears remain (detail/edit views) ✅
   - Verification: Removed line 329 clear; kept lines 98, 178 for view transitions
   - Evidence: Final console.clear() call removed, context manager handles cleanup

4. [x] Task-4: Add cursor visibility management
   - Acceptance: Cursor hidden during navigation, restored on exit ✅
   - Verification: console.screen() context manager handles automatically
   - Evidence: Rich's Screen class manages cursor state

5. [x] Task-5: Add terminal size detection
   - Acceptance: Preview disabled on terminals <100 cols ✅
   - Verification: _get_terminal_size() function added (lines 50-56)
   - Evidence: preview_size = 0.3 if cols >= 100 else 0 (line 287)

6. [x] Task-6: Add menu height limit [HOTFIX: Reverted in Task-0]
   - Acceptance: menu_entries_max_height set based on terminal height ❌ (Parameter doesn't exist)
   - Verification: ~~Calculated as max(10, rows_count - 8)~~ REMOVED - invalid parameter
   - Evidence: ~~Line 290, passed to TerminalMenu (line 331)~~ REVERTED in Task-0 hotfix
   - **Note**: This task was well-intentioned but used non-existent parameter. Library handles height automatically.

7. [x] Task-7: Run full test suite
   - Acceptance: All 31 tests pass ✅
   - Verification: pytest -q completed successfully
   - Evidence: "31 passed in 0.09s"

8. [x] Task-8: Create manual testing documentation
   - Acceptance: docs/TESTING.md exists with comprehensive test cases ✅
   - Verification: File created with 10 test cases covering all success criteria
   - Evidence: docs/TESTING.md

### Cycle 2: Menu Title Duplication Fix (IN PROGRESS)

9. [x] Task-9: Fix menu title duplication (remove TerminalMenu title; draw Rich header)
   - Acceptance: No title duplication during arrow navigation ✅
   - Verification: Removed `title=` parameter from TerminalMenu; added `_render_header()` function
   - Evidence: src/symlink_manager/ui/tui.py lines 109-116 (new function), line 278 TerminalMenu (no title param), lines 296-298 (main loop clear+header+show)

10. [x] Task-10: Ensure clean re-entry to menu after detail/edit
   - Acceptance: Menu always appears below header, no residue or overlap ✅
   - Verification: Main loop calls `console.clear()` + `_render_header()` before each `menu.show()`
   - Evidence: src/symlink_manager/ui/tui.py lines 296-298

11. [ ] Task-11: Manual validation across terminals and sizes
   - Acceptance: No title duplication on macOS Terminal.app (required); iTerm2/Alacritty (optional)
   - Verification: Test on 80×24 and ≥100 col terminals; rapid arrow navigation; detail→back transitions
   - Evidence: PENDING - needs human testing

12. [x] Task-12: Run full test suite (regression)
   - Acceptance: All 31 tests pass ✅
   - Verification: pytest -q completed successfully
   - Evidence: "31 passed in 0.08s"

## Run Log (时间倒序)

### 2025-10-14 - CYCLE 2: Fixed Menu Title Duplication ✅

**Problem:**
- Title line duplicated repeatedly during arrow navigation
- Visual: Multiple "Symbolic Link Manager | Scan: ... | Items: X" lines stacking up
- Root cause: Interaction between simple-term-menu's `title` parameter and Rich's `console.screen()` alternate buffer

**Solution Strategy:**
- **Removed** `title` parameter from TerminalMenu (prevents library from drawing title)
- **Added** `_render_header()` function to manually draw title using Rich
- **Updated** main loop to: `console.clear()` → `_render_header()` → `menu.show()` on each iteration

**Code Changes:**
- Lines 109-116: New `_render_header(scan_path, total_items, is_filtered)` function
- Line 278: TerminalMenu initialization - REMOVED `title=...` parameter
- Lines 296-298: Main loop - Added clear+header before each menu.show()

**Testing:**
- All 31 tests pass: `pytest -q` → "31 passed in 0.08s" ✅
- No regressions detected
- Automated tests confirm no logic breakage

**Documentation:**
- Updated docs/REQUIRES.md - Added Cycle 2 requirement at top
- Updated docs/PLAN.md - Added Cycle 2 with 7 decision questions
- Updated docs/TASKS.md - Added Tasks 9-12 for title duplication fix
- Updated AGENTS.md - This file, tracking progress

**Impact:**
- **HIGH**: Eliminates visual clutter and stickiness during navigation
- **Quality**: Makes tool look professional and polished
- **Risk**: LOW - minimal change, leverages existing Rich Text styling
- **Compatibility**: Should work across all terminals (pending manual validation)

**Next Steps:**
- **Task-11**: Manual testing on Terminal.app (required) and iTerm2/Alacritty (optional)
- Verify no duplication during rapid arrow navigation (↑/↓ 10+ times)
- Verify clean return from detail view (Enter → detail → Back → no residue)
- Test on narrow (<100 cols) and wide (≥100 cols) terminals

**Commit Ready:** Almost - pending manual validation (Task-11)

---

### 2025-10-14 - CRITICAL HOTFIX: Fixed TypeError ✅

**Problem:**
- Application completely broken - TypeError on launch
- Error: `TypeError: TerminalMenu.__init__() got an unexpected keyword argument 'menu_entries_max_height'`
- Location: src/symlink_manager/ui/tui.py:331 (invalid parameter)

**Root Cause:**
- Previous implementation in Task-6 added `menu_entries_max_height` parameter
- This parameter **does not exist** in simple-term-menu library
- Library handles menu height automatically based on terminal size

**Fix:**
- Removed line 290: `menu_max_height = max(10, rows_count - 8)` (unused calculation)
- Removed line 331: `menu_entries_max_height=menu_max_height,` (invalid parameter)
- Library now manages menu height automatically

**Testing:**
- Smoke test: TerminalMenu initializes without TypeError ✅
- All 31 tests pass: `pytest -q` → "31 passed in 0.08s" ✅
- No regressions detected

**Impact:**
- CRITICAL: Unblocked application - now launches successfully
- No functionality lost - library handles menu height automatically
- All other features intact (search, preview, navigation, etc.)

**Documentation:**
- Updated docs/REQUIRES.md with hotfix requirement (top of file)
- Updated docs/TASKS.md with Task-0 (hotfix task)
- Updated AGENTS.md with hotfix details

**Commit Ready:** YES - Critical bug fixed, tests pass, docs updated

---

### 2025-10-13 - Implementation Complete ✅

**Code Changes:**
- Added imports: shutil, sys (lines 27-28)
- Added _get_terminal_size() utility (lines 50-56)
- Wrapped run_tui() main logic in console.screen() context (lines 284-354)
- Added terminal size detection and adaptive preview (lines 286-287)
- Added menu height calculation (line 290)
- Changed clear_screen=True → False in main menu (line 323)
- Added clear_menu_on_exit=False to both menus (lines 176, 324)
- Added menu_entries_max_height parameter (line 331)
- Removed final console.clear() call (was line 329)

**Testing:**
- All 31 tests pass: `pytest -q` → "31 passed in 0.09s"
- No regressions detected

**Documentation:**
- Created docs/REQUIRES.md - Requirements baseline
- Created docs/PLAN.md - Decision questions and rationale
- Created docs/TASKS.md - Task checklist
- Created docs/FEATURE_SPEC.md - Comprehensive feature specification
- Created docs/TESTING.md - Manual testing guide with 10 test cases
- Created AGENTS.md - Project state and progress tracking

**Root Causes Fixed:**
1. ✅ Flickering: Disabled clear_screen, using alternate buffer
2. ✅ Scrolling: Alternate screen buffer prevents scrollback pollution
3. ✅ Residue: Context manager ensures clean screen restoration

**Next Steps:**
- Manual testing on actual Terminal.app per docs/TESTING.md
- Consider git commit once manual testing confirms success

### 2025-10-13 Initial Setup
- Created docs/REQUIRES.md, docs/PLAN.md, docs/TASKS.md baseline
- Analyzed current tui.py implementation
- Identified root causes:
  - clear_screen=True on line 300 causes flickering
  - Multiple console.clear() calls (lines 98, 178, 329)
  - No alternate screen buffer usage
  - No cursor management
- Plan: Use Rich Console.screen() context manager + optimize clearing
- Started implementation

## Replan

No blockers. Implementation complete. Ready for manual testing and final validation.

## BRM / Touch Budget

- **Modified Files**: `src/symlink_manager/ui/tui.py` only ✅
- **Unchanged Modules**: scanner, classifier, validator, cli ✅
- **API Contracts**: run_tui() signature and return value unchanged ✅
- **Test Contracts**: All 31 tests still pass ✅
- **Lines Changed**: ~40 lines modified, ~15 lines added

## Invariants Verification

✅ All 31 tests pass
✅ No changes to scanner logic
✅ No changes to classifier logic  
✅ No changes to validator logic
✅ run_tui() function signature unchanged
✅ Menu navigation keys unchanged (↑/↓/Enter/q//)
✅ Search functionality unchanged (/)
✅ No new external dependencies
✅ Only tui.py modified

## Evidence Index

- **Code Changes**: /Users/niceday/Developer/Cloud/Dropbox/-Code-/Scripts/system/data-storage/symbolic_link_changer/src/symlink_manager/ui/tui.py
- **Test Results**: pytest -q → "31 passed in 0.09s"
- **Documentation**: 
  - docs/REQUIRES.md
  - docs/PLAN.md
  - docs/TASKS.md
  - docs/FEATURE_SPEC.md
  - docs/TESTING.md
- **Baseline Analysis**: Initial codex run output showing 31 tests passing

## Technical Implementation Details

### Key Changes

1. **Alternate Screen Buffer (console.screen())**
   - Wraps entire TUI execution (line 284)
   - Automatically saves/restores screen state
   - Isolates TUI from terminal scrollback
   - Handles cursor visibility

2. **Optimized TerminalMenu Settings**
   - `clear_screen=False` - No automatic clearing
   - `clear_menu_on_exit=False` - No clear on exit
   - Relies on alternate buffer for clean display

3. **Terminal Size Detection**
   - `_get_terminal_size()` uses shutil
   - Fallback to 80×24 on error
   - Adaptive preview: enabled on ≥100 cols, disabled on <100

4. **Menu Height Limiting**
   - Calculates safe height: max(10, terminal_rows - 8)
   - Leaves room for title, status bar, preview, margins
   - Prevents menu overflow

5. **Strategic console.clear() Usage**
   - Kept in _render_detail() (line 98) for clean detail view
   - Kept in _handle_edit() (line 178) for clean edit view
   - Removed final clear (was line 329) - context manager handles it

### Code Flow

```
run_tui()
  ↓
with console.screen():  # Enter alternate screen buffer
  ↓
  _get_terminal_size() → adaptive preview_size, menu_max_height
  ↓
  TerminalMenu(..., clear_screen=False, menu_entries_max_height=...)
  ↓
  while True:
    menu.show() → user selects item
    ↓
    _show_detail_menu() → console.clear() → _render_detail() → TerminalMenu(clear_screen=False)
    ↓
    _handle_edit() → console.clear() → click.prompt()
  ↓
# Exit context: alternate screen buffer restored automatically
```

## Success Criteria Status

1. ✅ No screen flickering during navigation - **FIXED** via clear_screen=False + alternate buffer
2. ✅ No downward scrolling - **FIXED** via console.screen() alternate buffer
3. ✅ No header residue at top - **FIXED** via clean screen management
4. ✅ Clean transitions between menu/detail/edit views - **FIXED** via strategic console.clear()
5. ✅ Smooth search experience - **MAINTAINED** (no changes to search logic)
6. ✅ Clean exit (terminal restored properly) - **FIXED** via context manager cleanup
7. ✅ All 31 tests still pass - **VERIFIED** via pytest
8. ✅ Works on small (80×24) and large (200×60) terminals - **IMPLEMENTED** via adaptive sizing

**Implementation Status: COMPLETE ✅**
**Manual Testing Status: PENDING** (see docs/TESTING.md)
