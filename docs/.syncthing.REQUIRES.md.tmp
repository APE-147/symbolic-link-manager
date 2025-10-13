# REQUIRES

> 手动维护：记录最原始需求与应用场景；仅允许人工在顶部追加最新需求块；历史不得改写。

## 2025-10-13 - TUI Refactoring to simple-term-menu

### 原始需求
Refactor the TUI implementation to use `simple-term-menu` library instead of the current custom Rich-based terminal navigation.

### 应用场景
- 当前使用自定义的 termios/tty 原始终端模式处理
- 复杂的按键读取逻辑 (_read_key, _RawMode) 和手动光标追踪
- 手动视口计算和滚动指示器渲染
- 需要更稳定、功能更丰富、经过良好测试的菜单系统

### 目标
1. 用 `simple-term-menu` 替换自定义键盘导航实现
2. 减少 ~150-200 行复杂终端代码
3. 添加搜索功能 (按 `/` 搜索)
4. 添加预览面板功能
5. 改善用户体验和代码可维护性
6. 保持所有现有功能和测试通过 (33 tests)

### 约束
- CLI 接口保持不变 (用户无感知)
- 核心扫描/过滤/验证功能不变
- 性能要求: <500ms for 1000 symlinks
- 所有现有核心测试必须通过
- 分组显示逻辑保持不变 (classified projects first, unclassified last)

### 当前实现问题
- 自定义 termios/tty 原始终端处理 (~40 lines)
- 手动按键读取逻辑 (_read_key, _RawMode)
- 复杂的视口计算和滚动逻辑 (~100 lines)
- 自定义输入编辑器 (_prompt_input ~25 lines)
- 跨平台兼容性有限 (Unix-only)

### 预期收益
- 更少代码：从 ~500 行降至 ~300 行
- 内置搜索：按 `/` 过滤条目
- 内置预览面板：显示符号链接详情
- 更好的滚动：库管理的平滑滚动
- 更强的健壮性：经过良好测试的库
- 更好的跨平台支持
