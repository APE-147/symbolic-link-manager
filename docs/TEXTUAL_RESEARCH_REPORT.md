# Textual TUI 研究报告

> 研究 Chatlog (Go/tview) 的 TUI 实现模式，并映射到 Python/Textual 方案
>
> **日期**: 2025-10-14
> **目标**: 解决当前 simple-term-menu 的终端渲染残留问题
> **参考项目**: https://github.com/sjzar/chatlog

---

## 执行摘要

### 问题诊断
当前 symlink_manager 使用 **simple-term-menu** + **Rich**，存在以下渲染问题：
1. 闪烁和滚动污染（已通过 `console.screen()` 缓解）
2. 标题重复（已通过手动 Rich header 修复）
3. **根本原因**: simple-term-menu 不是为复杂布局设计的，缺乏虚拟 DOM 和状态管理

### 推荐方案
**迁移到 Textual** - Python 原生的现代化 TUI 框架，提供：
- 虚拟 DOM 和智能 diff 渲染（避免闪烁）
- 强大的布局系统（Grid/Container）
- Rich 集成（同一作者）
- AsyncIO 事件循环（类似 Go tcell）
- 活跃维护和完善文档

---

## 第一部分：Go tview/tcell 技术栈分析

### 1.1 tview/tcell 核心概念

#### 布局管理
**tview** 提供三种布局容器：

1. **Flex** - 灵活布局（类似 CSS Flexbox）
```go
flex := tview.NewFlex().
    SetDirection(tview.FlexRow).  // 行方向
    AddItem(header, 3, 0, false).  // 固定高度3行
    AddItem(contentFlex, 0, 1, true).  // 占据剩余空间（权重1）
    AddItem(footer, 1, 0, false)   // 固定高度1行

// 嵌套 Flex（列方向）
contentFlex := tview.NewFlex().
    AddItem(listView, 0, 1, true).    // 左侧列表（权重1）
    AddItem(detailView, 0, 3, false)  // 右侧详情（权重3）
```

2. **Grid** - 网格布局
```go
grid := tview.NewGrid().
    SetRows(3, 0, 1).       // 3行固定，中间自适应，底部1行
    SetColumns(30, 0, 30).  // 左30列，中间自适应，右30列
    AddItem(widget, row, col, rowSpan, colSpan, minWidth, minHeight, focus)
```

3. **Box** - 基础容器
- 所有 widget 的基类
- 提供边框、标题、颜色设置

#### 事件处理
**tcell** 提供底层终端事件循环：

```go
// 键盘事件绑定
app.SetInputCapture(func(event *tcell.EventKey) *tcell.EventKey {
    switch event.Key() {
    case tcell.KeyEscape:
        app.Stop()
        return nil  // 消费事件
    case tcell.KeyRune:
        if event.Rune() == 'q' {
            app.Stop()
            return nil
        }
    }
    return event  // 传递给下一个处理器
})

// 组件级别事件
list.SetInputCapture(func(event *tcell.EventKey) *tcell.EventKey {
    if event.Rune() == '/' {
        // 触发搜索
        return nil
    }
    return event
})
```

#### 渲染机制
**tview 的 Box.Draw() 模式**：
1. 每个 widget 实现 `Draw(screen tcell.Screen)` 方法
2. Application 维护 dirty flag 跟踪需要重绘的区域
3. 调用 `app.Draw()` 时只重绘脏区域
4. tcell 管理双缓冲，避免闪烁

```go
// 手动触发重绘
app.QueueUpdateDraw(func() {
    list.Clear()
    for _, item := range newItems {
        list.AddItem(item, "", 0, nil)
    }
})
```

#### 焦点管理
```go
// 设置焦点
app.SetFocus(listView)

// 焦点切换
flex.SetInputCapture(func(event *tcell.EventKey) *tcell.EventKey {
    if event.Key() == tcell.KeyTab {
        if currentFocus == listView {
            app.SetFocus(detailView)
        } else {
            app.SetFocus(listView)
        }
        return nil
    }
    return event
})
```

### 1.2 为何避免渲染残留？

**tview/tcell 的关键设计**：
1. **交替屏幕缓冲区** - tcell 默认使用 alternate screen
2. **虚拟屏幕抽象** - tcell.Screen 提供统一接口，底层管理缓冲区
3. **智能 diff** - 只发送变化的单元格到终端
4. **原子更新** - `screen.Show()` 原子性地刷新整个屏幕
5. **事件驱动** - 不手动清屏，依赖组件重绘

**对比当前问题**：
- simple-term-menu 调用 `print()` 和 ANSI 转义序列
- 缺乏脏区域跟踪
- 手动 `console.clear()` 导致整屏刷新

---

## 第二部分：Python Textual 技术映射

### 2.1 技术对应表

| Go tview/tcell | Python Textual | 说明 |
|---------------|---------------|------|
| `tview.Application` | `textual.app.App` | 主应用容器 |
| `tview.Flex` | `Horizontal` / `Vertical` | 灵活布局容器 |
| `tview.Grid` | `Grid` + CSS `grid-size` | 网格布局 |
| `tview.List` | `ListView` / `OptionList` | 列表控件 |
| `tview.Table` | `DataTable` | 表格控件 |
| `tview.TextView` | `Static` / `RichLog` | 静态文本显示 |
| `tview.InputField` | `Input` | 单行输入 |
| `tview.TextArea` | `TextArea` | 多行输入 |
| `tview.Modal` | `Screen` (modal mode) | 模态对话框 |
| `SetInputCapture()` | `on_key()` / `@on()` | 键盘事件绑定 |
| `app.SetFocus()` | `widget.focus()` | 焦点管理 |
| `app.Draw()` | 自动（虚拟 DOM） | 渲染触发 |
| `tcell.Screen` | Textual 内置渲染器 | 屏幕抽象 |
| `app.Run()` | `app.run()` (async) | 主循环启动 |

### 2.2 Textual 核心架构

#### 应用生命周期
```python
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static

class LKApp(App):
    """Symbolic Link Manager TUI"""

    CSS = """
    Screen {
        layout: vertical;
    }
    #main-container {
        layout: horizontal;
    }
    #symlink-list {
        width: 40%;
    }
    #detail-panel {
        width: 60%;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("/", "search", "Search"),
        ("e", "edit", "Edit"),
    ]

    def compose(self) -> ComposeResult:
        """创建 UI 结构"""
        yield Header()
        with Container(id="main-container"):
            yield SymlinkList(id="symlink-list")
            yield DetailPanel(id="detail-panel")
        yield Footer()

    def on_mount(self) -> None:
        """应用启动后执行"""
        self.query_one(SymlinkList).focus()
        self.load_symlinks()

    async def action_search(self) -> None:
        """搜索动作"""
        await self.push_screen(SearchScreen())

    async def action_edit(self) -> None:
        """编辑动作"""
        selected = self.query_one(SymlinkList).selected_item
        if selected:
            await self.push_screen(EditScreen(selected))
```

#### 布局系统
**1. CSS 驱动布局**（推荐 - 类似 Web 开发）
```python
# Python 代码
def compose(self) -> ComposeResult:
    yield Header()
    with Container(id="main"):
        yield ListView(id="list")
        yield Static(id="preview")
    yield Footer()

# CSS 文件或字符串
CSS = """
#main {
    layout: grid;
    grid-size: 2 1;  /* 2列 1行 */
    grid-columns: 1fr 2fr;  /* 左1份，右2份 */
}

#list {
    border: solid blue;
    height: 100%;
}

#preview {
    border: solid green;
    height: 100%;
}
"""
```

**2. 代码驱动布局**（灵活 - 类似 tview Flex）
```python
def compose(self) -> ComposeResult:
    yield Header()
    with Horizontal():  # 等价于 tview.FlexRow
        yield ListView(id="list", classes="box")
        with Vertical():  # 嵌套垂直布局
            yield Static("Detail", id="detail")
            yield Static("Preview", id="preview")
    yield Footer()
```

#### 事件处理
**键盘事件**：
```python
# 方法1：全局绑定（BINDINGS）
class LKApp(App):
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("j", "move_down", "Down"),
        ("k", "move_up", "Up"),
    ]

    def action_quit(self) -> None:
        self.exit()

    def action_move_down(self) -> None:
        self.query_one(ListView).move_cursor(1)

# 方法2：on_key 钩子
async def on_key(self, event: events.Key) -> None:
    if event.key == "slash":  # "/"
        await self.push_screen(SearchScreen())
    elif event.key == "e":
        await self.action_edit()
```

**组件事件**：
```python
# 监听 ListView 选择变化
@on(ListView.Selected)
def on_list_selected(self, event: ListView.Selected) -> None:
    """更新详情面板"""
    detail_panel = self.query_one(DetailPanel)
    detail_panel.update(event.item.data)
```

#### 屏幕管理（多视图导航）
```python
# 主屏幕
class MainListScreen(Screen):
    def compose(self) -> ComposeResult:
        yield ListView(id="symlinks")
        yield Footer()

    def on_list_item_selected(self, event) -> None:
        self.app.push_screen(DetailScreen(event.item))

# 详情屏幕
class DetailScreen(Screen):
    def __init__(self, symlink_info):
        super().__init__()
        self.symlink_info = symlink_info

    def compose(self) -> ComposeResult:
        yield Static(f"Path: {self.symlink_info.path}")
        yield Static(f"Target: {self.symlink_info.target}")
        yield Footer()

    def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            self.app.pop_screen()  # 返回上一屏

# 应用中使用
class LKApp(App):
    def on_mount(self) -> None:
        self.push_screen(MainListScreen())
```

#### 响应式属性（自动刷新）
```python
from textual.reactive import reactive

class SymlinkList(ListView):
    item_count = reactive(0)  # 响应式属性

    def watch_item_count(self, old_count, new_count) -> None:
        """当 item_count 改变时自动调用"""
        self.border_title = f"Symlinks ({new_count})"

    def add_symlink(self, info):
        self.append_item(...)
        self.item_count += 1  # 自动触发 watch_item_count
```

### 2.3 渲染优化机制

**Textual 如何避免闪烁？**

1. **虚拟 DOM（类似 React）**
   - 每次更新生成虚拟屏幕表示
   - Diff 算法计算最小变更集
   - 只刷新变化的区域

2. **智能脏区域跟踪**
```python
# 自动标记脏区域
widget.update("new content")  # 内部调用 refresh()
widget.styles.background = "blue"  # 自动触发重绘
```

3. **批量更新**
```python
async def update_list(self, items):
    list_view = self.query_one(ListView)
    with self.batch_update():  # 批量模式，减少重绘
        list_view.clear()
        for item in items:
            list_view.append_item(item)
    # 离开 with 块时一次性刷新
```

4. **交替屏幕缓冲区（内置）**
   - Textual 默认使用 alternate screen
   - 自动管理终端状态保存/恢复

---

## 第三部分：迁移架构设计

### 3.1 目标架构

```
LKApp (主应用)
├── MainListScreen (主屏幕)
│   ├── Header (标题栏)
│   ├── HierarchicalTree (三层级树)
│   │   ├── [PRIMARY] Desktop
│   │   │   ├── [SECONDARY] Projects
│   │   │   │   └── MyApp → /target
│   │   │   └── [SECONDARY] Archive
│   │   └── [PRIMARY] Service
│   ├── PreviewPanel (可选，宽屏显示)
│   └── Footer (快捷键提示)
├── DetailScreen (详情屏幕)
│   ├── Static: Path
│   ├── Static: Target
│   ├── Static: Validators
│   └── Footer
└── EditScreen (编辑屏幕)
    ├── Static: Instruction
    ├── Input: Target Path
    ├── Static: Validation Result
    └── Footer
```

### 3.2 组件映射

| 当前 (simple-term-menu) | 新设计 (Textual) | 实现方式 |
|------------------------|-----------------|---------|
| `TerminalMenu` 主菜单 | `Tree` or `DataTable` | 三层级可折叠树或带缩进的表格 |
| `_render_header()` | `Header` widget | 内置组件，自动布局 |
| `_build_rows()` | `Tree.add_node()` | 递归添加节点 |
| `_render_detail()` | `DetailScreen` | 独立 Screen |
| `_handle_edit()` | `EditScreen` | 独立 Screen + Input |
| `console.clear()` | 无需手动清屏 | 虚拟 DOM 自动处理 |
| `preview_size` 逻辑 | CSS Media Query | 响应式布局 |

### 3.3 数据流

```
CLI (cli.py)
  ↓
扫描 (scanner.scan_symlinks)
  ↓
分类 (classifier.classify_symlinks_auto_hierarchy)
  ↓
过滤 (filter_symlinks)
  ↓
传递给 TUI
  ↓
LKApp.symlinks (响应式属性)
  ↓
HierarchicalTree.update(symlinks)
  ↓
用户交互 (事件)
  ↓
DetailScreen / EditScreen
  ↓
编辑 → 更新数据 → 刷新主列表
```

---

## 第四部分：实施路线图

### Phase 1: 基础设施（任务-1 到 任务-2）

**任务-1: 引入 Textual 依赖**
```toml
[project.optional-dependencies]
textual = ["textual>=0.60,<1.0"]
```
- **验收**: `pip install -e .[textual]` 成功
- **测试**: `python -c "import textual; print(textual.__version__)"`

**任务-2: 创建骨架应用**
```python
# src/symlink_manager/ui/tui_textual.py
from textual.app import App
from textual.screen import Screen

class MainListScreen(Screen):
    def compose(self):
        yield Static("Main List Placeholder")

class DetailScreen(Screen):
    def compose(self):
        yield Static("Detail Placeholder")

class EditScreen(Screen):
    def compose(self):
        yield Static("Edit Placeholder")

class LKApp(App):
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("/", "search", "Search"),
        ("e", "edit", "Edit"),
    ]

    def on_mount(self):
        self.push_screen(MainListScreen())
```
- **验收**: `python -m symlink_manager.cli --ui-engine textual` 显示占位符
- **测试**: 按 `q` 能退出，无崩溃

### Phase 2: 主列表实现（任务-3）

**选项 A: 使用 Tree（推荐 - 更语义化）**
```python
from textual.widgets import Tree

class HierarchicalTree(Tree):
    def load_symlinks(self, hierarchical_data):
        self.clear()
        root = self.root

        for primary, secondaries in hierarchical_data.items():
            primary_node = root.add(f"[PRIMARY] {primary}", expand=True)

            for secondary, projects in secondaries.items():
                secondary_node = primary_node.add(f"  [SECONDARY] {secondary}", expand=True)

                for symlink in projects:
                    label = f"    {symlink.project_name} → {symlink.target}"
                    secondary_node.add_leaf(label, data=symlink)
```

**选项 B: 使用 DataTable（备选 - 更灵活）**
```python
from textual.widgets import DataTable

class HierarchicalTable(DataTable):
    def load_symlinks(self, hierarchical_data):
        self.clear(columns=True)
        self.add_column("Symlink", key="name")
        self.add_column("Target", key="target")

        for primary, secondaries in hierarchical_data.items():
            self.add_row(f"[PRIMARY] {primary}", "", key=f"p_{primary}")
            for secondary, projects in secondaries.items():
                self.add_row(f"  [SECONDARY] {secondary}", "", key=f"s_{secondary}")
                for symlink in projects:
                    self.add_row(
                        f"    {symlink.project_name}",
                        str(symlink.target),
                        key=str(symlink.path)
                    )
```

- **验收**: 加载真实数据后显示三层级
- **测试**: 展开/折叠功能正常，项目可选中

### Phase 3: 详情和编辑（任务-4）

**DetailScreen 实现**
```python
class DetailScreen(Screen):
    def __init__(self, symlink_info):
        super().__init__()
        self.info = symlink_info

    CSS = """
    DetailScreen {
        align: center middle;
    }
    #detail-container {
        width: 80%;
        height: auto;
        border: solid blue;
        padding: 1;
    }
    """

    def compose(self):
        with Container(id="detail-container"):
            yield Static(f"Path: {self.info.path}")
            yield Static(f"Target: {self.info.target}")
            yield Static(f"Primary: {self.info.primary_category}")
            yield Static(f"Secondary: {self.info.secondary_category}")
            yield Static(f"Project: {self.info.project_name}")
            yield Button("Edit", id="edit-btn")
            yield Button("Back", id="back-btn")

    @on(Button.Pressed, "#edit-btn")
    def on_edit(self):
        self.app.push_screen(EditScreen(self.info))

    @on(Button.Pressed, "#back-btn")
    def on_back(self):
        self.app.pop_screen()
```

**EditScreen 实现**
```python
class EditScreen(Screen):
    def __init__(self, symlink_info):
        super().__init__()
        self.info = symlink_info

    def compose(self):
        yield Static("Edit Target Path")
        yield Input(value=str(self.info.target), id="target-input")
        yield Static("", id="validation-msg")
        yield Button("Save", id="save-btn")
        yield Button("Cancel", id="cancel-btn")

    @on(Input.Changed, "#target-input")
    def on_input_changed(self, event):
        # 实时验证
        is_valid = self.validate_path(event.value)
        msg = self.query_one("#validation-msg")
        if is_valid:
            msg.update("[green]✓ Valid path[/]")
        else:
            msg.update("[red]✗ Invalid path[/]")

    @on(Button.Pressed, "#save-btn")
    def on_save(self):
        new_target = self.query_one("#target-input").value
        # TODO: 调用 services.update_symlink()
        self.app.pop_screen()

    @on(Button.Pressed, "#cancel-btn")
    def on_cancel(self):
        self.app.pop_screen()
```

- **验收**: Enter 进详情 → `e` 进编辑 → 输入验证 → 保存/取消返回
- **测试**: 错误输入有红色提示

### Phase 4: CLI 集成（任务-5）

```python
# src/symlink_manager/cli.py
@click.command()
@click.option("--ui-engine", type=click.Choice(["simple", "textual"]), default="simple")
def main(ui_engine, ...):
    if ui_engine == "textual":
        try:
            from symlink_manager.ui.tui_textual import LKApp
        except ImportError:
            click.echo("Error: Textual not installed. Run: pip install -e .[textual]")
            sys.exit(1)

        app = LKApp(symlinks=filtered_symlinks)
        app.run()
    else:
        # 现有 simple-term-menu 路径
        from symlink_manager.ui.tui import run_tui
        run_tui(filtered_symlinks, config, scan_root)
```

- **验收**: `--ui-engine simple|textual` 都能运行
- **测试**: 未安装 Textual 时有友好提示

### Phase 5: 测试（任务-6）

**Textual Pilot 测试示例**
```python
# tests/test_tui_textual_pilot.py
import pytest
pytest.importorskip("textual")  # 跳过如果未安装

from textual.pilot import Pilot
from symlink_manager.ui.tui_textual import LKApp

@pytest.mark.asyncio
async def test_navigation():
    app = LKApp()
    async with app.run_test() as pilot:
        # 等待应用启动
        await pilot.pause()

        # 按下键
        await pilot.press("down")
        await pilot.press("down")
        await pilot.press("enter")

        # 断言屏幕变化
        assert "DetailScreen" in str(pilot.app.screen)

        # 返回
        await pilot.press("escape")
        assert "MainListScreen" in str(pilot.app.screen)

@pytest.mark.asyncio
async def test_search():
    app = LKApp()
    async with app.run_test() as pilot:
        await pilot.press("/")
        await pilot.pause()
        # 断言搜索框可见
```

- **验收**: 关键交互路径可自动化测试
- **测试**: `pytest tests/test_tui_textual_pilot.py -v`

### Phase 6: 回归与验证（任务-7 到 任务-8）

**任务-7: 回归测试**
- 运行 `pytest -q`
- 确认 46+ 测试通过
- 验证 simple UI 路径仍正常

**任务-8: 渲染问题验证**
- 在 Terminal.app 80×24 测试
- 在 ≥100 列终端测试
- 快速按键（j/k 连续 20 次）
- 视图切换（主列表 ↔ 详情 ↔ 编辑）
- **预期**: 无闪烁、无标题重复、无滚动污染

---

## 第五部分：风险与缓解

### 5.1 风险评估

| 风险 | 影响 | 概率 | 缓解措施 |
|-----|------|------|---------|
| Textual 学习曲线陡峭 | 中 | 中 | 提供骨架代码和详细注释 |
| 性能问题（大数据集） | 中 | 低 | 使用虚拟滚动（DataTable 内置） |
| 终端兼容性问题 | 高 | 低 | Textual 支持主流终端，回退到 simple |
| 依赖冲突 | 低 | 低 | 使用 optional-dependencies 隔离 |
| 迁移不完整 | 高 | 中 | 保留 simple UI 作为回退 |

### 5.2 回退策略

1. **CLI 开关**: `--ui-engine simple` 始终可用
2. **渐进迁移**: 先实现只读功能，编辑功能后续加
3. **并行维护**: 两套 UI 共存 1-2 个版本周期
4. **监控指标**: 用户反馈、崩溃率、性能指标

---

## 第六部分：成功标准

### 6.1 功能验收

- [ ] 主列表显示三层级结构（Tree 或 DataTable）
- [ ] 支持折叠/展开（如使用 Tree）
- [ ] 键盘导航（↑/↓/j/k/Enter/Esc/q）
- [ ] 搜索功能（/）
- [ ] 详情视图（显示完整信息）
- [ ] 编辑视图（输入验证 + 保存/取消）
- [ ] 宽屏预览面板（可选）
- [ ] 状态栏和快捷键提示（Footer）

### 6.2 质量验收

- [ ] 无屏幕闪烁（连续导航 50 次）
- [ ] 无标题重复
- [ ] 无滚动污染
- [ ] 平滑视图切换（<100ms 感知延迟）
- [ ] 快速按键响应（无卡顿）
- [ ] 终端尺寸变化适应（resize 测试）
- [ ] 所有测试通过（≥46）

### 6.3 文档验收

- [ ] 更新 README（新 UI 引擎说明）
- [ ] 更新 TASKS.md（进度跟踪）
- [ ] 创建 docs/TEXTUAL_GUIDE.md（用户指南）
- [ ] 代码注释（关键组件说明）

---

## 第七部分：参考资源

### 官方文档
- Textual 官方文档: https://textual.textualize.io/
- Textual GitHub: https://github.com/Textualize/textual
- Rich 文档: https://rich.readthedocs.io/

### 示例项目
- Textual 官方示例: https://github.com/Textualize/textual/tree/main/examples
- Frogmouth (Markdown TUI): https://github.com/Textualize/frogmouth
- Textual Web (浏览器预览): https://textual.textualize.io/guide/devtools/

### 学习资源
- Textual 快速入门: https://textual.textualize.io/tutorial/
- Textual Discord 社区: https://discord.gg/Enf6Z3qhVr
- Will McGugan (作者) Twitter: @willmcgugan

---

## 附录 A：完整原型代码

```python
# src/symlink_manager/ui/tui_textual.py
"""
Textual-based TUI for Symbolic Link Manager
"""
from pathlib import Path
from typing import Dict, List

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    Header,
    Footer,
    Tree,
    Static,
    Input,
    Button,
)
from textual.binding import Binding
from textual import events, on

from symlink_manager.core.scanner import SymlinkInfo


class HierarchicalTree(Tree):
    """三层级符号链接树"""

    def load_data(self, hierarchical: Dict[str, Dict[str, List[SymlinkInfo]]]):
        """加载分层数据"""
        self.clear()
        root = self.root
        root.expand()

        for primary, secondaries in hierarchical.items():
            primary_node = root.add(
                f"[bold blue][PRIMARY][/] {primary}",
                data={"type": "primary", "name": primary},
                expand=True
            )

            for secondary, symlinks in secondaries.items():
                secondary_node = primary_node.add(
                    f"[bold green][SECONDARY][/] {secondary}",
                    data={"type": "secondary", "name": secondary},
                    expand=True
                )

                for symlink in symlinks:
                    project = symlink.project_name or "unknown"
                    target = symlink.target
                    secondary_node.add_leaf(
                        f"[cyan]{project}[/] → {target}",
                        data={"type": "symlink", "info": symlink}
                    )


class DetailScreen(Screen):
    """详情屏幕"""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("e", "edit", "Edit"),
    ]

    def __init__(self, symlink_info: SymlinkInfo):
        super().__init__()
        self.info = symlink_info

    CSS = """
    DetailScreen {
        align: center middle;
    }
    #detail-box {
        width: 80%;
        height: auto;
        border: solid blue;
        padding: 1 2;
    }
    .detail-label {
        color: $text-muted;
    }
    .detail-value {
        color: $text;
        margin-bottom: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="detail-box"):
            yield Static("[bold]Symlink Details[/]")
            yield Static("Path:", classes="detail-label")
            yield Static(str(self.info.path), classes="detail-value")
            yield Static("Target:", classes="detail-label")
            yield Static(str(self.info.target), classes="detail-value")
            yield Static("Primary:", classes="detail-label")
            yield Static(self.info.primary_category or "N/A", classes="detail-value")
            yield Static("Secondary:", classes="detail-label")
            yield Static(self.info.secondary_category or "N/A", classes="detail-value")
            yield Static("Project:", classes="detail-label")
            yield Static(self.info.project_name or "N/A", classes="detail-value")

            with Horizontal():
                yield Button("Edit (e)", id="edit-btn", variant="primary")
                yield Button("Back (Esc)", id="back-btn")
        yield Footer()

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_edit(self) -> None:
        self.app.push_screen(EditScreen(self.info))

    @on(Button.Pressed, "#edit-btn")
    def on_edit_pressed(self) -> None:
        self.action_edit()

    @on(Button.Pressed, "#back-btn")
    def on_back_pressed(self) -> None:
        self.action_back()


class EditScreen(Screen):
    """编辑屏幕"""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, symlink_info: SymlinkInfo):
        super().__init__()
        self.info = symlink_info

    CSS = """
    EditScreen {
        align: center middle;
    }
    #edit-box {
        width: 80%;
        height: auto;
        border: solid green;
        padding: 1 2;
    }
    #validation-msg {
        height: 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="edit-box"):
            yield Static("[bold]Edit Target Path[/]")
            yield Static(f"Current: {self.info.target}")
            yield Input(
                value=str(self.info.target),
                placeholder="Enter new target path",
                id="target-input"
            )
            yield Static("", id="validation-msg")

            with Horizontal():
                yield Button("Save", id="save-btn", variant="success")
                yield Button("Cancel (Esc)", id="cancel-btn")
        yield Footer()

    def action_cancel(self) -> None:
        self.app.pop_screen()

    @on(Input.Changed, "#target-input")
    def on_input_changed(self, event: Input.Changed) -> None:
        """实时验证输入"""
        msg = self.query_one("#validation-msg", Static)
        path = Path(event.value)

        if not event.value:
            msg.update("[yellow]⚠ Path cannot be empty[/]")
        elif not path.is_absolute():
            msg.update("[yellow]⚠ Path must be absolute[/]")
        elif path.exists():
            msg.update("[green]✓ Valid path[/]")
        else:
            msg.update("[red]✗ Path does not exist[/]")

    @on(Button.Pressed, "#save-btn")
    def on_save(self) -> None:
        new_target = self.query_one("#target-input", Input).value
        # TODO: 调用 services.update_symlink(self.info.path, new_target)
        self.notify(f"TODO: Save {new_target}")
        self.app.pop_screen()

    @on(Button.Pressed, "#cancel-btn")
    def on_cancel(self) -> None:
        self.action_cancel()


class MainListScreen(Screen):
    """主列表屏幕"""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("/", "search", "Search"),
        Binding("j", "move_down", "Down"),
        Binding("k", "move_up", "Up"),
    ]

    def __init__(self, hierarchical_data: Dict):
        super().__init__()
        self.hierarchical_data = hierarchical_data

    CSS = """
    MainListScreen {
        layout: vertical;
    }
    #tree-container {
        height: 100%;
        border: solid blue;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="tree-container"):
            yield HierarchicalTree("Symbolic Links", id="symlink-tree")
        yield Footer()

    def on_mount(self) -> None:
        tree = self.query_one(HierarchicalTree)
        tree.load_data(self.hierarchical_data)
        tree.focus()

    @on(Tree.NodeSelected)
    def on_tree_selected(self, event: Tree.NodeSelected) -> None:
        """处理节点选择"""
        node_data = event.node.data
        if node_data and node_data.get("type") == "symlink":
            symlink_info = node_data["info"]
            self.app.push_screen(DetailScreen(symlink_info))

    def action_quit(self) -> None:
        self.app.exit()

    def action_search(self) -> None:
        # TODO: 实现搜索屏幕
        self.notify("Search not implemented yet")

    def action_move_down(self) -> None:
        tree = self.query_one(HierarchicalTree)
        tree.action_cursor_down()

    def action_move_up(self) -> None:
        tree = self.query_one(HierarchicalTree)
        tree.action_cursor_up()


class LKApp(App):
    """Symbolic Link Manager - Textual TUI"""

    CSS = """
    Screen {
        background: $surface;
    }
    """

    def __init__(self, hierarchical_data: Dict, **kwargs):
        super().__init__(**kwargs)
        self.hierarchical_data = hierarchical_data

    def on_mount(self) -> None:
        self.push_screen(MainListScreen(self.hierarchical_data))


# 入口函数（从 CLI 调用）
def run_textual_tui(hierarchical_data: Dict):
    """启动 Textual TUI"""
    app = LKApp(hierarchical_data)
    app.run()
```

---

## 附录 B：时间估算

| 阶段 | 任务 | 估算时间 | 依赖 |
|-----|------|---------|------|
| Phase 1 | 任务-1: 引入依赖 | 15 分钟 | 无 |
| Phase 1 | 任务-2: 骨架应用 | 1 小时 | 任务-1 |
| Phase 2 | 任务-3: 主列表 | 2 小时 | 任务-2 |
| Phase 3 | 任务-4: 详情编辑 | 2.5 小时 | 任务-3 |
| Phase 4 | 任务-5: CLI 集成 | 1 小时 | 任务-4 |
| Phase 5 | 任务-6: Pilot 测试 | 2 小时 | 任务-5 |
| Phase 6 | 任务-7: 回归测试 | 30 分钟 | 任务-6 |
| Phase 6 | 任务-8: 渲染验证 | 1 小时 | 任务-7 |
| **总计** | | **10.25 小时** | |

**建议**: 分 2-3 天完成，每天 3-4 小时专注工作。

---

**报告完成日期**: 2025-10-14
**作者**: codex-feature agent
**版本**: 1.0
