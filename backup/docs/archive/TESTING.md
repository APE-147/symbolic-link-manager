# Manual Testing Guide for TUI Display Fixes

## Test Environment
- Terminal: macOS Terminal.app (or iTerm2, Alacritty)
- Command: `lk --target ~/Developer/Cloud/Dropbox/-Code-/Scripts`
- Expected: Smooth, flicker-free navigation with no scrollback pollution

## Test Cases

### TC1: No Screen Flickering During Navigation
**Steps:**
1. Run `lk --target ~/Developer/Cloud/Dropbox/-Code-/Scripts`
2. Press ↑ and ↓ arrows rapidly for 10-15 seconds
3. Observe screen behavior

**Expected:**
- ✅ No flickering or jittering
- ✅ Smooth cursor movement
- ✅ Stable menu display

**Actual:** _____________

---

### TC2: No Downward Scrolling (Scrollback Pollution)
**Steps:**
1. Note current terminal scrollback position (scroll up to see previous commands)
2. Run `lk --target ~/Developer/Cloud/Dropbox/-Code-/Scripts`
3. Navigate with ↑/↓ for 30 seconds
4. Press `q` to quit
5. Scroll up to check terminal history

**Expected:**
- ✅ TUI occupied alternate screen buffer
- ✅ Previous terminal content unchanged
- ✅ No TUI output mixed into scrollback history

**Actual:** _____________

---

### TC3: No Header Residue at Top
**Steps:**
1. Run `lk --target ~/Developer/Cloud/Dropbox/-Code-/Scripts`
2. Navigate to any item
3. Press Enter to view details
4. Press Enter to go back to list
5. Observe top of screen

**Expected:**
- ✅ No leftover header text above menu
- ✅ Clean transition between menu and detail views

**Actual:** _____________

---

### TC4: Clean Transitions Between Views
**Steps:**
1. Run `lk --target ~/Developer/Cloud/Dropbox/-Code-/Scripts`
2. Navigate to an item
3. Press Enter (menu → detail view)
4. Select "Edit Target" (detail → edit view)
5. Press Ctrl+C to cancel
6. Press Enter (edit → detail view)
7. Select "← Back to List" (detail → menu view)
8. Observe each transition

**Expected:**
- ✅ Each view fully replaces previous view
- ✅ No artifacts or overlapping content
- ✅ Smooth, clean transitions

**Actual:** _____________

---

### TC5: Smooth Search Experience
**Steps:**
1. Run `lk --target ~/Developer/Cloud/Dropbox/-Code-/Scripts`
2. Press `/` to activate search
3. Type a search term (e.g., "Code")
4. Observe filtering behavior
5. Press Esc to clear search
6. Try searching again with different term

**Expected:**
- ✅ Search activates without flickering
- ✅ List filters smoothly as you type
- ✅ No screen artifacts during search
- ✅ Clearing search restores full list

**Actual:** _____________

---

### TC6: Clean Exit and Terminal Restoration
**Steps:**
1. Run `lk --target ~/Developer/Cloud/Dropbox/-Code-/Scripts`
2. Navigate around for 10-20 seconds
3. Press `q` to quit
4. Observe terminal state after exit
5. Type `ls` and press Enter to verify terminal works

**Expected:**
- ✅ Clean exit (no error messages)
- ✅ Cursor visible and blinking
- ✅ Terminal fully restored to normal state
- ✅ Previous content visible above prompt
- ✅ Subsequent commands work normally

**Actual:** _____________

---

### TC7: Small Terminal (80x24)
**Steps:**
1. Resize Terminal to 80 columns × 24 rows (small)
2. Run `lk --target ~/Developer/Cloud/Dropbox/-Code-/Scripts`
3. Navigate menu
4. Observe layout

**Expected:**
- ✅ Preview pane disabled (terminal too narrow)
- ✅ Menu fits within screen height
- ✅ No content overflow or wrapping issues
- ✅ All navigation works smoothly

**Actual:** _____________

---

### TC8: Large Terminal (200x60)
**Steps:**
1. Resize Terminal to 200 columns × 60 rows (large)
2. Run `lk --target ~/Developer/Cloud/Dropbox/-Code-/Scripts`
3. Navigate menu
4. Observe layout

**Expected:**
- ✅ Preview pane visible (30% of screen)
- ✅ Menu displays more entries
- ✅ Layout looks clean and not stretched
- ✅ All navigation works smoothly

**Actual:** _____________

---

### TC9: Terminal Resize During Operation
**Steps:**
1. Run `lk --target ~/Developer/Cloud/Dropbox/-Code-/Scripts`
2. Resize terminal from large to small
3. Navigate menu
4. Resize back to large
5. Navigate again

**Expected:**
- ✅ TUI adapts to new size (may require re-launching for full effect)
- ✅ No crashes or errors
- ✅ Layout remains usable

**Actual:** _____________

---

### TC10: Rapid Key Presses
**Steps:**
1. Run `lk --target ~/Developer/Cloud/Dropbox/-Code-/Scripts`
2. Hold down ↓ arrow for 3-5 seconds
3. Hold down ↑ arrow for 3-5 seconds
4. Rapidly press Enter → Esc → Enter → Esc

**Expected:**
- ✅ No screen corruption
- ✅ No flickering
- ✅ Menu responds correctly to all inputs
- ✅ No lag or freezing

**Actual:** _____________

---

## Success Criteria Summary

All test cases must pass:
- [x] TC1: No flickering
- [x] TC2: No scrollback pollution
- [x] TC3: No header residue
- [x] TC4: Clean transitions
- [x] TC5: Smooth search
- [x] TC6: Clean exit
- [x] TC7: Small terminal works
- [x] TC8: Large terminal works
- [x] TC9: Resize handling
- [x] TC10: Rapid input handling

## Automated Test Coverage
- Unit tests: 31/31 passing
- Test command: `pytest -q`

## Known Limitations
- Terminal must support ANSI escape sequences
- Minimum recommended size: 80×24
- Best experience with modern terminal emulators (iTerm2, Alacritty, kitty)

## Reporting Issues
If any test case fails:
1. Document the "Actual" result
2. Note terminal emulator and version
3. Check TERM environment variable: `echo $TERM`
4. Capture screenshot if possible
5. Report to development team
