# Quick Testing Guide: Textual TUI

## Prerequisites

```bash
# Install Textual (if not already installed)
pip install -e .[textual]

# Verify installation
python -c "import textual; print(f'Textual {textual.__version__}')"
```

## Basic Launch

```bash
# Launch with Textual TUI (default scan path: ~/Developer/Cloud/Dropbox/-Code-)
lk --ui-engine textual

# Specify custom scan path
lk --ui-engine textual --target ~/Desktop

# With filtering options
lk --ui-engine textual --target ~/Desktop --include-garbled --files
```

## Keyboard Shortcuts

### Main List Screen
- `↑`/`k` - Move up
- `↓`/`j` - Move down
- `Enter` - Open detail view
- `/` - Search (placeholder, shows notification)
- `q` - Quit

### Detail Screen
- `e` - Edit target
- `Esc` - Back to list

### Edit Screen
- Type to edit target path
- Watch real-time validation (colors change)
- `Esc` - Cancel
- Click "Save" - Save changes (currently shows TODO notification)

## Rendering Problem Verification

**This is the KEY test to verify the fix:**

### Test 1: Fast Navigation
1. Launch TUI: `lk --ui-engine textual --target ~/Desktop`
2. Hold down `↓` or `j` for 2 seconds
3. **Observe**: Cursor should move smoothly with **NO flickering or residue**
4. ✅ PASS if: No visual artifacts
5. ❌ FAIL if: Screen flickers, text duplicates, or residue appears

### Test 2: Screen Switching
1. Launch TUI
2. Press `Enter` (open detail)
3. Press `Esc` (back to list)
4. Repeat 5-10 times rapidly
5. **Observe**: Transitions should be smooth and clean
6. ✅ PASS if: No residue between screen switches
7. ❌ FAIL if: Previous screen content remains visible

### Test 3: Terminal Resize
1. Launch TUI
2. Resize terminal window (drag corner)
3. **Observe**: Layout should adapt automatically
4. ✅ PASS if: Content reflows without artifacts
5. ❌ FAIL if: Broken layout or rendering glitches

## Comparison Test (Old vs New)

### Test with simple-term-menu (old)
```bash
lk --ui-engine simple --target ~/Desktop
# Navigate and observe rendering
```

### Test with Textual (new)
```bash
lk --ui-engine textual --target ~/Desktop
# Navigate and compare
```

**Expected Improvement**: Textual should have **zero flickering** where simple-term-menu had issues.

## Development Mode (Advanced)

```bash
# Run with Textual DevTools (shows live console)
textual run --dev src/symlink_manager/ui/tui_textual.py

# Or via CLI wrapper (requires code modification)
# Add: app.run(headless=False) in run_textual_ui()
```

## Known Issues (Expected)

1. **Search shows notification**: "Search not implemented yet" - This is expected (Phase 3)
2. **Save shows TODO**: Edit → Save shows "TODO: Save {path}" - This is expected (Phase 3)
3. **No undo/redo**: Edit operations are not tracked yet - Future enhancement

## Troubleshooting

### Error: "textual is not installed"
```bash
pip install -e .[textual]
```

### TUI doesn't start
```bash
# Check Python version (requires 3.9+)
python --version

# Check module can be imported
python -c "from symlink_manager.ui.tui_textual import run_textual_ui"
```

### No symlinks found
```bash
# Check scan path exists
ls ~/Desktop

# Try with broader filters
lk --ui-engine textual --target ~/Desktop --include-garbled --files --no-filter
```

## Success Criteria

After testing, Phase 2 is successful if:

- ✅ TUI launches without errors
- ✅ Tree displays 3-level hierarchy
- ✅ Navigation is responsive (j/k/arrows)
- ✅ Detail screen shows correct information
- ✅ Edit screen has input field with validation
- ✅ **NO rendering residue during fast navigation** (KEY)
- ✅ **NO flickering during screen switches** (KEY)

## Reporting Issues

If you encounter problems:

1. Note the exact command used
2. Describe what happened vs what you expected
3. Include terminal size (echo $COLUMNS x $LINES)
4. Include Textual version (python -c "import textual; print(textual.__version__)")
5. Try with `--dev` mode for more diagnostics

---

**Ready to test?** Run: `lk --ui-engine textual --target ~/Desktop`
