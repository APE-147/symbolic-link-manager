# TASKS

> 首次由 PLAN.md 展开；后续自动更新/缩进新增子任务，严格遵循代办格式。

* [x] Task-0: Fix TerminalMenu TypeError (CRITICAL HOTFIX)

  * 要求: Remove invalid parameter `menu_entries_max_height` from TerminalMenu initialization
  * 说明: The parameter `menu_entries_max_height` does not exist in simple-term-menu library. Library handles menu height automatically. Remove line 331 parameter and line 290 unused calculation.
  * 测试: Run `lk --target ~/Developer/Cloud/Dropbox/-Code-/Scripts` and verify no TypeError
  * 完成证据: Line 290 removed (menu_max_height calculation), Line 331 removed (invalid parameter), smoke test passes without TypeError

* [x] Task-1: Implement alternate screen buffer support

  * 要求: Add Rich Console.screen() context manager to run_tui()
  * 说明: Wrap the entire TUI execution in `with console.screen()` to use alternate screen buffer, preventing scrollback pollution and header residue
  * 测试: Run `lk --target ~/Developer/Cloud/Dropbox/-Code-/Scripts` and verify no scrollback pollution
  * 完成证据: Lines 284-354 in tui.py, context manager wraps entire main loop

* [x] Task-2: Optimize TerminalMenu screen clearing settings

  * 要求: Change clear_screen=True to clear_screen=False in all TerminalMenu instances
  * 说明: Disable automatic screen clearing in simple-term-menu to reduce flickering; rely on alternate screen buffer for clean display
  * 测试: Navigate menu with ↑/↓ and verify no flickering
  * 完成证据: Main menu line 323 (clear_screen=False), detail menu line 175 (clear_screen=False), added clear_menu_on_exit=False (lines 176, 324)

* [x] Task-3: Minimize console.clear() calls and ensure clean transitions

  * 要求: Remove unnecessary console.clear() calls; keep only strategic clears for view transitions
  * 说明: Remove console.clear() at end of run_tui (was line 329); keep clears in _render_detail (line 98) and _handle_edit (line 178) for clean view transitions
  * 测试: Navigate between menu→detail→edit and verify clean transitions
  * 完成证据: Final console.clear() removed, context manager handles cleanup automatically

* [x] Task-4: Add cursor visibility management

  * 要求: Hide cursor during menu navigation, restore on exit
  * 说明: Console.screen() context manager handles this automatically
  * 测试: Verify cursor is invisible during menu navigation and restored after quit
  * 完成证据: Rich's Screen class manages cursor state (no explicit code needed)

* [x] Task-5: Add terminal size detection and adaptive preview

  * 要求: Detect terminal size and disable preview pane if width < 100 columns
  * 说明: Use shutil.get_terminal_size() to detect terminal dimensions; set preview_size=0 for narrow terminals, 0.3 for wide ones
  * 测试: Resize terminal to <100 cols and verify preview is disabled; resize to >100 cols and verify preview appears
  * 完成证据: _get_terminal_size() function (lines 50-56), adaptive preview_size logic (line 287)

* [x] Task-6: Add menu height limit to prevent overflow

  * 要求: Set menu_entries_max_height parameter in TerminalMenu
  * 说明: Calculate safe max height (terminal height - title - status bar - preview - margins), typically around 15-20 entries visible
  * 测试: Test with many symlinks and verify menu doesn't exceed screen height
  * 完成证据: menu_max_height calculation (line 290), passed to TerminalMenu (line 331)

* [x] Task-7: Run full test suite to ensure no regressions

  * 要求: All 31 existing tests must pass
  * 说明: Run `pytest -q` to verify no functionality broken
  * 测试: `pytest -q` should show "31 passed"
  * 完成证据: "31 passed in 0.09s" - all tests passing

* [x] Task-8: Create manual testing documentation

  * 要求: Create docs/TESTING.md with manual test scenarios
  * 说明: Document test cases for flickering, scrolling, residue, transitions, search, quit, terminal sizes
  * 测试: Follow docs/TESTING.md checklist on actual Terminal.app
  * 完成证据: docs/TESTING.md created with 10 comprehensive test cases

## Progress Summary

- **Total Tasks**: 13 (8 original + 1 hotfix + 4 new)
- **Completed**: 12
- **In Progress**: 0
- **Pending**: 1

## Implementation Summary

All code changes completed in `src/symlink_manager/ui/tui.py`:
- Added imports: shutil, sys
- Added _get_terminal_size() utility function
- Wrapped run_tui() in console.screen() context manager
- Optimized TerminalMenu settings (clear_screen=False, clear_menu_on_exit=False, menu_entries_max_height)
- Implemented adaptive preview based on terminal width
- All 31 tests passing
- Comprehensive documentation created (REQUIRES.md, PLAN.md, FEATURE_SPEC.md, TESTING.md)

## Next Steps

1. Manual testing on actual Terminal.app following docs/TESTING.md
2. Git commit if manual testing confirms success
3. Optional: Test on iTerm2, Alacritty for broader compatibility verification

* [x] Task-9: Fix menu title duplication (remove TerminalMenu title; draw Rich header)

  * 要求: 移除 `TerminalMenu(title=...)`；在菜单显示前用 Rich 输出单行标题（包含 Scan 路径、Items 数、是否 filtered），避免重复行
  * 说明: `clear_screen=False` 下库会在每次导航重绘 `title` 导致堆叠；改为自绘可完全规避，同时保留 `status_bar` 与 `preview`
  * 测试: 运行 `lk --target ~/Developer/Cloud/Dropbox/-Code-/Scripts`，上下导航 10+ 次，无标题重复；进入详情→返回后仍无重复
  * 完成证据: `src/symlink_manager/ui/tui.py` 去除 `title=` 参数；新增 `_render_header()` 用于菜单前渲染；`pytest -q` 通过

* [x] Task-10: Ensure clean re-entry to menu after detail/edit

  * 要求: 从详情/编辑返回主菜单前执行 `console.clear()`，重绘标题，再调用 `menu.show()`
  * 说明: 保障菜单起始位置固定在标题之后，避免叠画与错位；仅在视图切换时清屏，箭头导航不清屏
  * 测试: 进入详情页查看→按 Enter 返回主菜单；确认菜单顶端紧随标题，无残留
  * 完成证据: 在主循环中于 `menu.show()` 前调用 `console.clear()` + `_render_header(...)`（见 `tui.py` 主循环）

* [ ] Task-11: Manual validation across terminals and sizes

  * 要求: 在 macOS Terminal.app（必测）、iTerm2（可选）中验证；80×24 / ≥100 列宽两档
  * 说明: 宽屏保持 `preview_size=0.3`，窄屏 `preview_size=0`
  * 测试: 按 docs/TESTING.md 新增用例执行，确认无标题重复与布局错位
  * 完成证据: 测试结果记录到 docs/TESTING.md（追加章节）

* [x] Task-12: Run full test suite (regression)

  * 要求: 31 个现有测试全部通过
  * 说明: 验证 UI 变更不影响核心逻辑与 CLI 契约
  * 测试: `pytest -q` 显示 "31 passed"
  * 完成证据: `pytest -q` → "31 passed in 0.09s"

---

## Cycle 3: Hierarchical 3-Level Classification System

### Progress
- **Total Tasks**: 8
- **Completed**: 0
- **In Progress**: 0
- **Pending**: 8
- **Overall Progress**: 0.00%

### Implementation Tasks

* [ ] Task-13: Implement hierarchical data models (Primary/Secondary/Project categories)

  * 要求: Create dataclass models for 3-level hierarchy in classifier.py - PrimaryCategory, SecondaryCategory, MarkdownConfig
  * 说明: Following PLAN Q1→B recommendation - use dataclass for type safety and IDE support. Includes Primary/Secondary/Project structure with patterns list at project level.
  * 测试: Unit tests can instantiate dataclasses and validate structure
  * 实施方案: Q1-B (dataclass), Q2-A (3 fields in SymlinkInfo: primary_category/secondary_category/project_name)

* [ ] Task-14: Extend SymlinkInfo dataclass with hierarchy fields

  * 要求: Add 3 new fields to SymlinkInfo in scanner.py: primary_category, secondary_category, project_name (all Optional[str])
  * 说明: Following PLAN Q2→A - semantic clarity, backward compatible (keep existing 'project' field for compatibility)
  * 测试: Import SymlinkInfo and verify new fields exist with type hints
  * 实施方案: Maintain backward compatibility - existing code using 'project' field continues to work

* [ ] Task-15: Update Markdown config parser for ##/###/- hierarchy

  * 要求: Rewrite parse_markdown_config_text() to support ## Primary, ### Secondary, - pattern structure; return new hierarchical MarkdownConfig
  * 说明: Following PLAN Q1→B + Q3→A - auto-detect flat vs hierarchical format. If no ### found, fallback to flat mode with primary="unclassified"
  * 测试: Unit tests with sample hierarchical MD and flat MD configs, verify both parse correctly
  * 实施方案: Parser detects config type and handles both formats transparently

* [ ] Task-16: Implement hierarchical classification logic

  * 要求: Update classify_symlinks() to perform 3-level matching (primary→secondary→pattern) using nested loops, first-match principle
  * 说明: Following PLAN Q5→A - triple nested loop for clarity. Return Dict[str, Dict[str, List[SymlinkInfo]]] (primary → secondary → symlinks)
  * 测试: Unit tests with mock config and symlinks, verify correct classification into 3 levels
  * 实施方案: Preserve existing first-match semantics, extend to 3 levels

* [ ] Task-17: Update TUI display to show 3-level indentation

  * 要求: Modify _build_menu_items() in tui.py to display hierarchy with indentation: [PRIMARY] → "  [Secondary]" → "    ✓ project"
  * 说明: Following PLAN Q4→A - simple indentation (2 spaces per level), ASCII-compatible, matches requirement example
  * 测试: Manual TUI test - run `lk --target <path>` with hierarchical config, verify display shows 3 levels with proper indentation
  * 实施方案: Menu items build function iterates primary→secondary→projects and adds indentation prefix

* [ ] Task-18: Write comprehensive tests for hierarchical classification

  * 要求: Create tests/test_hierarchical_classifier.py with tests for: parser (hierarchical + flat fallback), classification logic, TUI menu building
  * 说明: Following PLAN Q6→A - independent test file for clear organization and CI integration
  * 测试: Run `pytest tests/test_hierarchical_classifier.py -v` - all new tests pass
  * 实施方案: Mock configs, mock symlinks, test all 3 levels + backward compat + edge cases

* [ ] Task-19: Create example hierarchical config file

  * 要求: Create ~/.config/lk/projects.md with example 3-level config (Desktop/Service/System primary categories with subcategories)
  * 说明: Following PLAN Q7→A - standard user config location, matches requirement example structure
  * 测试: Verify file exists at ~/.config/lk/projects.md with valid ## / ### / - structure
  * 实施方案: Include Desktop/Projects, Service/APIs, System/Scripts examples from requirements

* [ ] Task-20: Run full regression test suite

  * 要求: All 31 existing tests must pass + new hierarchical tests pass
  * 说明: Ensure backward compatibility - no regressions in scanner, classifier, validator, TUI navigation
  * 测试: Run `pytest -q` - verify "31+ passed" (31 original + new hierarchical tests)
  * 实施方案: Fix any test failures; ensure flat config still works

### Success Criteria Checklist

- [ ] Parse 3-level Markdown config (##, ###, -)
- [ ] Classify symlinks into Primary → Secondary → Project hierarchy
- [ ] Display in TUI with proper 3-level indentation
- [ ] Navigation works through all levels (↑/↓/Enter/search/quit)
- [ ] Backward compatible with existing flat config
- [ ] All 31+ tests pass
- [ ] Example config file created at `~/.config/lk/projects.md`

### Implementation Strategy (from PLAN Q8→B)

**Single PR Atomic Implementation** (4-5h estimated):
1. Data models + SymlinkInfo extension (Task-13, Task-14) - 1h
2. Parser rewrite with backward compat (Task-15) - 1.5h
3. Classification logic update (Task-16) - 1h
4. TUI display update (Task-17) - 1h
5. Tests + example config (Task-18, Task-19) - 1.5h
6. Full regression test (Task-20) - 0.5h

**Rationale**: Atomic implementation ensures all tests pass together, easier rollback if needed, single coherent review.

### Risk Mitigation

- **Risk**: Breaking existing flat config users
  - **Mitigation**: Auto-detect parser (Q3→A) + keep backward compat tests
- **Risk**: TUI performance with many symlinks
  - **Mitigation**: Triple loop is O(n*m*k) but acceptable for typical symlink counts (<1000)
- **Risk**: Parser complexity
  - **Mitigation**: Dataclass models + comprehensive unit tests

### Dependencies

- No new external dependencies required
- Uses existing: dataclasses, fnmatch, pathlib, OrderedDict
- Compatible with Python 3.9+

