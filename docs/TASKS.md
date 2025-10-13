# TASKS

> 首次由 PLAN.md 展开；后续自动更新/缩进新增子任务，严格遵循代办格式。

## TUI Refactoring to simple-term-menu (Cycle 4)

* [ ] Task-1: Add simple-term-menu dependency

  * 要求: Add `simple-term-menu>=1.6.0` to pyproject.toml dependencies
  * 说明: Small, well-tested library for terminal menus with built-in search and preview
  * 测试命令: `pip install -e . && python -c "import simple_term_menu; print('OK')"`

* [ ] Task-2: Create backup branch and savepoint

  * 要求: Create git branch and tag before major refactoring
  * 说明: Ensure we can easily rollback if issues arise during refactoring
  * 测试命令: `git branch feat/tui-simple-term-menu && git tag savepoint/2025-10-13-before-stm-refactor`

* [ ] Task-3: Refactor run_tui() to use simple-term-menu

  * 要求: Replace custom terminal handling with TerminalMenu from simple-term-menu
  * 说明: Build menu items with group headers (non-selectable), configure preview, search, and styling
  * 核心功能:
    - Build flat menu list with `[PROJECT]` headers and item entries
    - Map menu index to SymlinkInfo objects
    - Configure TerminalMenu with search_key="/", preview_command, cycle_cursor
    - Handle selection and quit
  * 测试命令: `lk --target /tmp/test_symlinks` (manual verification)

* [ ] Task-4: Implement preview function for menu

  * 要求: Create `_generate_preview(item: SymlinkInfo) -> str` function
  * 说明: Generate formatted preview text showing name, location, target, status
  * 格式:
    - Name: {item.name}
    - Location: {item.path}
    - Target: {item.target}
    - Status: Valid/BROKEN
  * 测试命令: Manual TUI testing with preview pane visible

* [ ] Task-5: Implement detail view and action menu

  * 要求: Create `_show_detail_menu()` function using Rich Panel + TerminalMenu for actions
  * 说明: Show detailed info when Enter pressed, offer actions: Back/Edit/Quit
  * 核心功能:
    - Reuse existing `_render_detail()` for display
    - Create action menu: ["← Back to List", "Edit Target", "Quit"]
    - Return action string to main loop
  * 测试命令: Manual - press Enter on item, verify detail panel + action menu

* [ ] Task-6: Replace _prompt_input with click.prompt

  * 要求: Use click.prompt() for edit target input, remove custom _prompt_input
  * 说明: Simplify input handling, reduce ~25 lines of code
  * 核心功能:
    - Use `click.prompt("New target path", default=str(item.target))`
    - Validate with existing `validate_target_change()`
    - Show validation results
  * 测试命令: Manual - press 'e' to edit, verify click.prompt works

* [ ] Task-7: Remove custom terminal handling code

  * 要求: Delete _RawMode, _read_key, _calculate_viewport_size, _calculate_visible_range, _prompt_input
  * 说明: Remove ~165 lines of custom terminal code, all handled by simple-term-menu
  * 删除列表:
    - `_RawMode` class (~15 lines)
    - `_read_key()` function (~25 lines)
    - `_calculate_viewport_size()` (~15 lines)
    - `_calculate_visible_range()` (~50 lines)
    - `_prompt_input()` (~25 lines)
    - Scroll indicator logic in `_render_list()` (~35 lines)
  * 测试命令: `pytest tests/ -v` (ensure no broken imports)

* [ ] Task-8: Update test_tui_alignment.py tests

  * 要求: Refactor tests to focus on data structures (_build_rows) not rendering
  * 说明: Test that buckets are correctly flattened into rows with headers
  * 测试重点:
    - Verify `_build_rows()` creates headers before groups
    - Verify "unclassified" group appears last
    - Verify row.kind is correct ("header" vs "item")
  * 测试命令: `pytest tests/test_tui_alignment.py -v`

* [ ] Task-9: Run full test suite

  * 要求: Ensure all core tests still pass (scanner, classifier, filter, validator)
  * 说明: TUI refactoring should not affect core business logic
  * 预期结果: ≥30 tests pass (current 33 tests, some alignment tests may be updated)
  * 测试命令: `pytest tests/ -v --cov=src/symlink_manager`

* [ ] Task-10: Manual TUI testing with real symlinks

  * 要求: Test with actual symlink directories to verify UX
  * 说明: Verify all features work: navigation, search (/), preview, detail view, edit flow
  * 测试场景:
    - Large list (100+ symlinks) - verify smooth scrolling
    - Search with '/' - verify filtering works
    - Preview pane - verify info is correct
    - Edit target - verify click.prompt and validation
    - Quit with 'q' or Esc
  * 测试命令: `lk --target /Users/niceday/Developer/Cloud/Dropbox/-Code-`

* [ ] Task-11: Update documentation

  * 要求: Update README.md with new search feature, update CHANGELOG.md
  * 说明: Document that users can press '/' to search, preview pane auto-shows
  * 文件:
    - README.md: Add search feature to features list
    - CHANGELOG.md: Add entry for TUI refactoring
  * 测试命令: Review docs for accuracy

---

## Progress Calculation

Total tasks: 11
Completed: 0
Progress: 0.00%

## Notes

- All core business logic (scanner, classifier, validator) remains unchanged
- CLI interface (`lk` command) remains unchanged
- Grouping logic (classified first, unclassified last) preserved
- Performance should improve (library is well-optimized)
- Code reduction: ~200 lines removed, cleaner codebase
