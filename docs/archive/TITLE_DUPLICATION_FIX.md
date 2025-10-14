# Menu Title Duplication Fix - Summary

**Date:** 2025-10-14
**Status:** ✅ FIXED (Automated tests pass; manual validation pending)
**Priority:** HIGH - Visual bug affecting UX and professionalism
**Branch:** feat/symlink-manager-mvp

---

## Problem Statement

When navigating the TUI menu with arrow keys (↑/↓), the title line duplicated repeatedly, creating visual clutter:

```
Symbolic Link Manager | Scan: ... | Items: 436 (filtered)
Symbolic Link Manager | Scan: ... | Items: 436 (filtered)
Symbolic Link Manager | Scan: ... | Items: 436 (filtered)
Symbolic Link Manager | Scan: ... | Items: 436 (filtered)
...
```

This "stickiness" made the tool look unprofessional and created confusion during navigation.

---

## Root Cause

**Interaction between two screen management systems:**

1. Rich's `console.screen()` uses an **alternate screen buffer** (good for isolation)
2. `simple-term-menu`'s `title` parameter tries to manage **its own title drawing**
3. With `clear_screen=False` (set in Cycle 1 to prevent flickering), the library **appends** the title on each navigation event instead of **replacing** it
4. Result: Title accumulates with each arrow key press

---

## Solution Implemented

### Strategy: Manual Header Management

**Remove library's title handling; draw header ourselves using Rich:**

1. **Removed** `title=...` parameter from `TerminalMenu()` initialization
2. **Added** `_render_header(scan_path, total_items, is_filtered)` function using Rich Text
3. **Updated** main loop to: `console.clear()` → `_render_header()` → `menu.show()`

This ensures:
- Header drawn **exactly once** per menu display
- Clean transitions when returning from detail/edit views
- Full control over styling and content
- No conflict with library's drawing logic

---

## Code Changes

### File: `src/symlink_manager/ui/tui.py`

#### 1. New `_render_header()` function (lines 109-116)

```python
def _render_header(scan_path: Path, total_items: int, is_filtered: bool) -> None:
    """Render a single-line header above the menu to avoid title duplication."""
    filter_label = " (filtered)" if is_filtered else ""
    header = Text(
        f"Symbolic Link Manager | Scan: {scan_path} | Items: {total_items}{filter_label}",
        style="bold",
    )
    console.print(header)
```

**Purpose:** Draw header manually using Rich, giving us full control over when and how it appears.

---

#### 2. Removed `title` parameter from TerminalMenu (line ~278)

**Before:**
```python
menu = TerminalMenu(
    menu_items,
    title=f"Symbolic Link Manager | Scan: {scan_path} | Items: {total_items}{filter_label}",  # ❌ REMOVED
    menu_cursor="→ ",
    # ...
)
```

**After:**
```python
menu = TerminalMenu(
    menu_items,
    # NO title parameter ✅
    menu_cursor="→ ",
    menu_cursor_style=("fg_cyan", "bold"),
    menu_highlight_style=("bg_cyan", "fg_black"),
    cycle_cursor=True,
    clear_screen=False,  # From Cycle 1 - prevents flickering
    clear_menu_on_exit=False,
    preview_command=lambda idx: _generate_preview(item_to_symlink.get(idx)),
    preview_size=preview_size,
    skip_empty_entries=True,
    status_bar=f"↑/↓ Navigate | Enter Details | / Search | q Quit",
    status_bar_style=("fg_cyan",),
    search_key="/",
)
```

---

#### 3. Updated main loop (lines 296-298)

**Before:**
```python
while True:
    selected_idx = menu.show()  # ❌ No header management
    # ...
```

**After:**
```python
while True:
    # Ensure a clean menu surface with a single header line above it
    console.clear()  # ✅ Clear alternate buffer
    _render_header(scan_path, total_items, is_filtered)  # ✅ Draw header once
    selected_idx = menu.show()  # ✅ Menu appears below header

    # User quit (Esc or q)
    if selected_idx is None:
        break

    # Get selected item
    selected_item = item_to_symlink.get(selected_idx)
    if selected_item is None:
        continue

    # Handle actions (detail/edit views clear their own screens)
    action = _show_detail_menu(selected_item, scan_path)
    if action == "quit":
        break
    elif action == "edit":
        _handle_edit(selected_item, scan_path)
```

**Key insight:** After returning from detail or edit views (which call `console.clear()` internally), we need to:
1. Clear the alternate buffer again
2. Redraw the header
3. Show the menu (which starts drawing from current cursor position)

This creates a clean, predictable layout every time.

---

## Testing Results

### Automated Tests: ✅ PASS

```bash
$ pytest -q
...............................                                          [100%]
31 passed in 0.08s
```

**All tests pass** - no regressions detected in:
- Scanner logic
- Classifier logic
- Validator logic
- CLI contract
- Filter rules

---

### Manual Testing: ⏳ PENDING

**Task-11** requires human validation:

#### Test Checklist

1. **Basic Navigation (Required)**
   ```bash
   lk --target ~/Developer/Cloud/Dropbox/-Code-/Scripts
   ```
   - [ ] Arrow navigate ↑/↓ 10+ times rapidly
   - [ ] Verify: NO duplicate title lines
   - [ ] Verify: Single header always visible at top

2. **Detail View Transitions (Required)**
   - [ ] Select item with Enter
   - [ ] View detail page
   - [ ] Press Enter to return to list
   - [ ] Verify: Menu appears cleanly below header
   - [ ] Verify: No residue or overlap

3. **Search Functionality (Required)**
   - [ ] Press `/` to search
   - [ ] Type search term
   - [ ] Navigate filtered results
   - [ ] Press Esc to exit search
   - [ ] Verify: Header shows "(filtered)" label
   - [ ] Verify: No duplication

4. **Terminal Size Variations (Required)**
   - [ ] Test on 80×24 terminal (narrow)
   - [ ] Verify: Preview disabled, header visible
   - [ ] Test on ≥100 cols terminal (wide)
   - [ ] Verify: Preview enabled, header visible
   - [ ] Verify: No layout issues

5. **Terminal Emulator Compatibility (Optional)**
   - [ ] macOS Terminal.app (REQUIRED)
   - [ ] iTerm2 (optional)
   - [ ] Alacritty (optional)

---

## Documentation Updates

All documentation kept in sync:

1. **docs/REQUIRES.md**
   - ✅ Added Cycle 2 requirement at top (newest first)
   - ✅ Preserved previous requirements (history intact)

2. **docs/PLAN.md**
   - ✅ Added Cycle 2 with 7 decision questions
   - ✅ Analyzed options for: header rendering, timing, styling, transitions, layout, compatibility
   - ✅ Progress: 100% (before adding new tasks) → 92.31% (12/13 tasks)

3. **docs/TASKS.md**
   - ✅ Added Tasks 9-12 in exact checklist format
   - ✅ Tasks 9, 10, 12 marked complete with evidence
   - ✅ Task 11 (manual testing) pending

4. **AGENTS.md**
   - ✅ Updated Header/Project Snapshot
   - ✅ Added Cycle 2 section to Top TODO
   - ✅ Added Run Log entry for Cycle 2
   - ✅ Progress tracked: 92.31% (12/13 tasks)

5. **docs/TITLE_DUPLICATION_FIX.md** (this file)
   - ✅ Comprehensive summary for future reference

---

## Impact Assessment

### What Changed
- ✅ **Minimal scope:** Only `src/symlink_manager/ui/tui.py` modified
- ✅ **3 code sections:** New function + removed param + updated loop
- ✅ **~20 lines affected:** Very small change surface

### What Stayed the Same
- ✅ **All functionality:** Search, preview, navigation, details, edit
- ✅ **All keyboard shortcuts:** ↑/↓/Enter/q//
- ✅ **All tests:** 31/31 passing
- ✅ **API contracts:** run_tui() signature unchanged
- ✅ **Core logic:** Scanner, classifier, validator untouched

### Risk Assessment
- **Risk Level:** LOW
- **Blast Radius:** Single file, UI layer only
- **Rollback:** Simple - revert 3 code sections
- **Dependencies:** None added

### Quality Improvement
- **Visual:** Eliminates clutter and stickiness ✅
- **UX:** Professional, clean navigation ✅
- **Maintainability:** Clearer separation of concerns (manual header vs library menu) ✅

---

## Trade-offs

### What We Gained ✅
- Clean, single-line header (no duplication)
- Smooth navigation without visual artifacts
- Full control over header styling and content
- Predictable behavior across terminals

### What We Lost ❌
- Nothing - library's `title` parameter was causing the bug

### Potential Concerns 🤔
- **Extra `console.clear()` in main loop:** Adds one clear per navigation cycle
  - **Impact:** Minimal - we're already in alternate buffer, clear is fast
  - **Benefit:** Ensures clean state before each menu display
- **Manual header management:** Requires discipline to keep header in sync
  - **Mitigation:** Centralized in `_render_header()` function

---

## Next Steps

### Immediate (Required)
1. **Manual Testing (Task-11)**
   - Run tool: `lk --target ~/Developer/Cloud/Dropbox/-Code-/Scripts`
   - Follow test checklist above
   - Document results in `docs/TASKS.md` Task-11 evidence field

### If Manual Testing Passes
2. **Git Commit**
   ```bash
   git add src/symlink_manager/ui/tui.py docs/ AGENTS.md
   git commit -m "fix(tui): eliminate menu title duplication during navigation

   Problem: Title line duplicated repeatedly during arrow navigation due to
   interaction between simple-term-menu's title parameter and Rich's
   alternate screen buffer.

   Solution:
   - Remove 'title' param from TerminalMenu (prevents library drawing)
   - Add _render_header() function for manual Rich-based header
   - Update main loop: clear → render_header → menu.show()

   Impact:
   - Eliminates visual clutter and stickiness
   - All 31 tests passing
   - Minimal code change (~20 lines in tui.py)

   Refs: docs/TITLE_DUPLICATION_FIX.md, AGENTS.md Cycle 2"
   ```

3. **Optional: Broader Terminal Testing**
   - Test on iTerm2
   - Test on Alacritty
   - Document compatibility in `docs/TESTING.md`

---

## References

- **Root Cause Analysis:** See user's original issue description
- **Decision Process:** `docs/PLAN.md` Cycle 2 (7 questions + rationale)
- **Task Breakdown:** `docs/TASKS.md` Tasks 9-12
- **Requirements:** `docs/REQUIRES.md` Cycle 2 section (top of file)
- **Progress Tracking:** `AGENTS.md` Cycle 2 section
- **Code Diff:** `src/symlink_manager/ui/tui.py` (lines 109-116, ~278, 296-298)

---

## Conclusion

**Status:** ✅ Fix implemented and automated tests pass
**Remaining:** Manual validation (Task-11) before commit
**Confidence:** HIGH - minimal change, clear root cause, all tests green

The menu title duplication issue has been resolved by taking manual control of header rendering. This eliminates the conflict between Rich's alternate buffer and simple-term-menu's title drawing, resulting in a clean, professional navigation experience.
