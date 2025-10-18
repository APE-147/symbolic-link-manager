# REQUIRES

> 手动维护：记录最原始需求与应用场景；仅允许人工在顶部追加最新需求块；历史不得改写。

## Latest Requirement (2025-10-14 16:30) - TUI Framework Refactoring to Textual

### 原始需求
当前使用 simple-term-menu + Rich 实现 TUI，存在终端渲染残留(粘黏行)问题。虽然已做初步修复，但希望参考 Chatlog(Go项目)使用更成熟的TUI框架彻底解决。

### 应用场景
- 符号链接管理工具的交互式终端界面
- 三层级分类浏览(Primary → Secondary → Project)
- 查看详情、编辑目标、搜索过滤
- 多终端尺寸适配

### 技术选型
- 目标框架: Textual (Python对应Go tview的最佳选择)
- 由Rich作者开发，无缝集成现有Rich库
- 现代化API(async/await)，活跃维护

### 核心要求
- 彻底解决渲染残留问题
- 保持所有44个现有测试通过
- 功能完全对标现有TUI
- 支持渐进式迁移(并行实现→完全替换)

### 实施策略
1. 并行实现: 保留tui.py，新增tui_textual.py
2. CLI提供 --ui-engine=simple|textual 选项
3. 默认使用simple，测试通过后切换到textual
4. 验收通过后删除simple-term-menu依赖

### 验收标准
- [ ] Textual实现功能完整对标现有TUI
- [ ] 无终端渲染残留/粘黏行问题
- [ ] 所有44个测试通过
- [ ] 性能无明显下降
- [ ] 代码质量符合项目标准

### 优先级
HIGH - 技术债务修复，提升用户体验质量

---

## Previous Requirement (2025-10-14 14:00) - Hierarchical 3-Level Classification System

### User Need
Implement a hierarchical 3-level classification system for symlink organization to better manage large numbers of symlinks across different categories.

### Current State
- System uses flat 1-level classification
- Users with many symlinks find it difficult to organize and navigate
- Configuration format is basic and lacks hierarchy
- Working branch: feat/symlink-manager-mvp
- All 31 tests passing

### Desired Outcome
- 3-level hierarchy: Primary Categories (Level 1) → Folder Categories (Level 2) → Projects (Level 3)
- Enhanced Markdown configuration format with ## / ### / - structure
- TUI display with proper indentation showing all three levels
- Backward compatible with existing flat configuration
- Example: Desktop/Projects/ProjectAlpha structure

### Application Scenarios
1. **Developer Workspace**: Organize development projects by type (Desktop/Service/System)
2. **Multi-Project Management**: Group related projects under logical folders
3. **Service Organization**: Separate APIs, Workers, and other service types
4. **System Administration**: Categorize scripts, configs, and system tools

### Success Criteria
- Parse 3-level Markdown config (##, ###, -)
- Classify symlinks into Primary → Secondary → Project hierarchy
- Display in TUI with proper indentation
- Navigation works through all levels
- All tests pass
- Example config file created at `~/.config/lk/projects.md`

### Priority
HIGH - Significant feature enhancement that improves organization for users with many symlinks

---

## Previous Requirement (2025-10-14 11:00) - Menu Title Duplication Bug

### Problem Statement
When navigating the menu with arrow keys in the TUI, the title line duplicates repeatedly, creating visual clutter and "stickiness" during navigation. Multiple header lines appear:

```
Symbolic Link Manager | Scan: ... | Items: 436 (filtered)
Symbolic Link Manager | Scan: ... | Items: 436 (filtered)
Symbolic Link Manager | Scan: ... | Items: 436 (filtered)
...
```

### Root Cause
Interaction between `simple-term-menu` and Rich's `console.screen()` context manager:
1. `console.screen()` uses alternate screen buffer
2. `simple-term-menu` also tries to manage screen clearing/positioning
3. The `title` parameter in TerminalMenu causes redraw issues in alternate buffer
4. Each navigation event triggers a redraw that appends instead of replacing

### Application Context
- Tool: Symbolic Link Manager TUI
- File: src/symlink_manager/ui/tui.py
- Current state: Working MVP on feat/symlink-manager-mvp branch (all previous issues fixed)
- Impact: Visual bug making tool look unprofessional

### Success Criteria
1. No duplicate title lines during navigation
2. Smooth, clean display updates
3. No visual stickiness or residue
4. All navigation works (↑/↓, search, details)
5. All 31 tests still pass

### Priority
HIGH - Visual bug affecting user experience and tool professionalism

---

## Previous Requirement (2025-10-14) - TerminalMenu TypeError Hotfix

### Problem
Fix TypeError in TerminalMenu initialization that prevents the application from launching.

**Error:** `TypeError: TerminalMenu.__init__() got an unexpected keyword argument 'menu_entries_max_height'`

**Location:** `src/symlink_manager/ui/tui.py:331` (invalid parameter) and line 290 (unused calculation)

**Root Cause:** The parameter `menu_entries_max_height` does not exist in the `simple-term-menu` library. The library automatically manages menu height based on terminal size and does not expose a parameter to limit it.

### User Impact
- **CRITICAL Priority** - Application completely broken, cannot launch
- Blocks all functionality - users cannot use the tool at all
- Error occurs immediately on startup: `lk --target <path>`

### Success Criteria
1. Application launches without TypeError
2. Menu displays correctly
3. Navigation works (up/down arrows, Enter, search, quit)
4. All existing functionality intact
5. No regressions in test suite

### Resolution
- **Fix 1:** Remove invalid parameter `menu_entries_max_height=menu_max_height` from line 331
- **Fix 2:** Remove unused variable calculation `menu_max_height = max(10, rows_count - 8)` from line 290
- **Verification:** TerminalMenu now initializes successfully without TypeError
- **Testing:** Manual smoke test confirms no TypeError; library handles menu height automatically

---

## Previous Requirement (2025-10-13)

### Problem
Fix terminal display issues in the TUI (Text User Interface) when running `lk` command:

1. **Screen flickering/jittering** - Display shakes or flashes during navigation
2. **Excessive downward scrolling** - Menu keeps pushing down, creating scrollback pollution
3. **Header residue at top** - First line/header remains visible above the menu after navigation

### User Impact
- **HIGH Priority** - Critical UX issue making the tool frustrating to use
- Users expect smooth, flicker-free TUI navigation like vim, less, htop

### Environment
- Terminal: macOS Terminal.app
- Current implementation: simple-term-menu library
- Working branch: feat/symlink-manager-mvp
- All 31 tests passing

### Success Criteria
1. No screen flickering during navigation
2. No downward scrolling (stays in same screen position)
3. No header residue at top
4. Clean transitions between menu/detail/edit views
5. Smooth search experience
6. Clean exit (terminal restored properly)
7. All 31 tests still pass
8. Works on small (80x24) and large (200x60) terminals

### Application Scenario
User runs: `lk --target /Users/username/Developer/Cloud/Dropbox/-Code-/Scripts`
Navigates with ↑/↓, enters details with Enter, searches with /, quits with q
Expects: Smooth, stable display without flicker or scrolling issues
