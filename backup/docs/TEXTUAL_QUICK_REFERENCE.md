# Textual 快速参考：Go tview → Python Textual 映射

> **速查表** - 用于快速查找 tview 概念在 Textual 中的等价实现
>
> **日期**: 2025-10-14
> **目标**: 加速从 Go/tview 到 Python/Textual 的迁移

---

## 📋 核心概念映射

| Go tview/tcell | Python Textual | 用途 |
|---------------|---------------|------|
| `tview.Application` | `textual.app.App` | 主应用容器 |
| `tview.Flex` | `Horizontal` / `Vertical` | 灵活布局（行/列） |
| `tview.Grid` | `Grid` + CSS | 网格布局 |
| `tview.Box` | `Widget` | 基础组件类 |
| `tview.List` | `ListView` / `OptionList` | 列表选择 |
| `tview.Tree` | `Tree` | 树形结构 |
| `tview.Table` | `DataTable` | 表格数据 |
| `tview.TextView` | `Static` / `RichLog` | 文本显示 |
| `tview.InputField` | `Input` | 单行输入 |
| `tview.TextArea` | `TextArea` | 多行编辑 |
| `tview.Modal` | `Screen` (modal) | 对话框 |
| `tview.Pages` | `Screen` stack | 多视图管理 |

---

## 🏗️ 布局系统对比

### Go tview: Flex 布局

```go
// 垂直布局（行方向）
flex := tview.NewFlex().
    SetDirection(tview.FlexRow).
    AddItem(header, 3, 0, false).      // 固定3行
    AddItem(content, 0, 1, true).      // 占满剩余（权重1）
    AddItem(footer, 1, 0, false)       // 固定1行

// 水平布局（列方向）
contentFlex := tview.NewFlex().
    AddItem(leftPanel, 0, 1, true).    // 左侧（权重1）
    AddItem(rightPanel, 0, 2, false)   // 右侧（权重2）
```

### Python Textual: Container 布局

```python
# 方法1: 使用容器嵌套
def compose(self) -> ComposeResult:
    with Vertical():                    # 垂直容器
        yield Header()                  # 固定高度
        with Horizontal():              # 水平容器
            yield LeftPanel()           # 自动布局
            yield RightPanel()
        yield Footer()                  # 固定高度

# 方法2: 使用 CSS 控制
CSS = """
Vertical {
    height: 100%;
}
LeftPanel {
    width: 1fr;  /* 权重1 */
}
RightPanel {
    width: 2fr;  /* 权重2 */
}
"""
```

---

## 🎨 样式与外观

### Go tview: 边框和颜色

```go
box.SetBorder(true).
    SetTitle("My Title").
    SetBorderColor(tcell.ColorBlue).
    SetTitleColor(tcell.ColorWhite).
    SetBackgroundColor(tcell.ColorBlack)
```

### Python Textual: CSS 样式

```python
# Python 代码
class MyWidget(Static):
    pass

# CSS 字符串或文件
CSS = """
MyWidget {
    border: solid blue;
    border-title: "My Title";
    background: black;
    color: white;
}
"""
```

---

## 🔧 事件处理对比

### Go tview: SetInputCapture

```go
// 应用级别
app.SetInputCapture(func(event *tcell.EventKey) *tcell.EventKey {
    if event.Key() == tcell.KeyEscape {
        app.Stop()
        return nil  // 消费事件
    }
    return event  // 传递事件
})

// 组件级别
list.SetInputCapture(func(event *tcell.EventKey) *tcell.EventKey {
    if event.Rune() == '/' {
        showSearchDialog()
        return nil
    }
    return event
})
```

### Python Textual: 事件绑定

```python
# 方法1: BINDINGS 类属性
class MyApp(App):
    BINDINGS = [
        ("escape", "quit", "Quit"),
        ("slash", "search", "Search"),
    ]

    def action_quit(self) -> None:
        self.exit()

    def action_search(self) -> None:
        self.push_screen(SearchScreen())

# 方法2: on_key 钩子
async def on_key(self, event: events.Key) -> None:
    if event.key == "escape":
        self.exit()
        event.prevent_default()  # 消费事件
```

---

## 🖱️ 组件事件

### Go tview: 选择回调

```go
list.SetSelectedFunc(func(index int, mainText string, secondaryText string, shortcut rune) {
    showDetail(index)
})

table.SetSelectedFunc(func(row, col int) {
    cellContent := table.GetCell(row, col).Text
    processCell(cellContent)
})
```

### Python Textual: 消息处理

```python
# 方法1: @on 装饰器
from textual import on

@on(ListView.Selected)
def on_list_selected(self, event: ListView.Selected) -> None:
    self.show_detail(event.item)

@on(DataTable.CellSelected)
def on_cell_selected(self, event: DataTable.CellSelected) -> None:
    cell_value = event.value
    self.process_cell(cell_value)

# 方法2: 命名约定
def on_list_view_selected(self, event: ListView.Selected) -> None:
    """自动绑定到 ListView.Selected 事件"""
    pass
```

---

## 🚪 多视图管理

### Go tview: Pages

```go
pages := tview.NewPages()
pages.AddPage("main", mainView, true, true)
pages.AddPage("detail", detailView, true, false)
pages.AddPage("edit", editView, true, false)

// 切换页面
pages.SwitchToPage("detail")

// 显示模态对话框
pages.AddPage("modal", modal, true, true)
```

### Python Textual: Screen Stack

```python
# 定义屏幕
class MainScreen(Screen):
    pass

class DetailScreen(Screen):
    def __init__(self, item_id):
        super().__init__()
        self.item_id = item_id

# 导航
self.push_screen(DetailScreen(item_id=123))  # 进入详情
self.pop_screen()                            # 返回上一屏

# 模态对话框
self.push_screen(ConfirmDialog(), callback=self.on_confirmed)
```

---

## 🎯 焦点管理

### Go tview

```go
app.SetFocus(listView)

// 在组件间切换
if currentFocus == listView {
    app.SetFocus(detailView)
}
```

### Python Textual

```python
# 设置焦点
self.query_one(ListView).focus()

# 切换焦点
if self.focused == self.query_one(ListView):
    self.query_one(DetailPanel).focus()

# 通过 Tab 键自动切换（CSS）
CSS = """
ListView {
    can-focus: true;
}
DetailPanel {
    can-focus: true;
}
"""
```

---

## 🔄 数据更新与渲染

### Go tview: 手动刷新

```go
// 更新后手动触发重绘
app.QueueUpdateDraw(func() {
    list.Clear()
    for _, item := range newItems {
        list.AddItem(item, "", 0, nil)
    }
})
```

### Python Textual: 响应式属性

```python
from textual.reactive import reactive

class MyList(ListView):
    item_count = reactive(0)  # 响应式属性

    def watch_item_count(self, old, new) -> None:
        """值改变时自动调用"""
        self.border_title = f"Items ({new})"

    def add_item(self, item):
        self.append(item)
        self.item_count += 1  # 自动触发刷新
```

---

## 📐 Grid 布局详解

### Go tview: NewGrid

```go
grid := tview.NewGrid().
    SetRows(3, 0, 1).        // 3行固定，中间自适应，底部1行
    SetColumns(30, 0, 30).   // 左30列，中间自适应，右30列
    AddItem(widget, row, col, rowSpan, colSpan, minWidth, minHeight, focus)

// 示例：标题+内容+底栏
grid.AddItem(header, 0, 0, 1, 3, 0, 0, false).  // 占满顶部3列
    AddItem(left, 1, 0, 1, 1, 0, 0, true).      // 左侧面板
    AddItem(content, 1, 1, 1, 1, 0, 0, false).  // 中间内容
    AddItem(right, 1, 2, 1, 1, 0, 0, false).    // 右侧面板
    AddItem(footer, 2, 0, 1, 3, 0, 0, false)    // 占满底部3列
```

### Python Textual: CSS Grid

```python
# Python 代码
def compose(self) -> ComposeResult:
    yield Header(id="header")
    yield LeftPanel(id="left")
    yield ContentArea(id="content")
    yield RightPanel(id="right")
    yield Footer(id="footer")

# CSS 样式
CSS = """
Screen {
    layout: grid;
    grid-size: 3 3;  /* 3列 3行 */
    grid-columns: 30 1fr 30;  /* 左30，中自适应，右30 */
    grid-rows: 3 1fr 1;       /* 顶3，中自适应，底1 */
}

#header {
    column-span: 3;  /* 占3列 */
}

#footer {
    column-span: 3;
}

#left {
    row: 2;
    column: 1;
}

#content {
    row: 2;
    column: 2;
}

#right {
    row: 2;
    column: 3;
}
"""
```

---

## 🌳 Tree 控件对比

### Go tview

```go
tree := tview.NewTree()
root := tview.NewTreeNode("Root").SetColor(tcell.ColorRed)
tree.SetRoot(root)

child1 := tview.NewTreeNode("Child 1")
child1.AddChild(tview.NewTreeNode("Leaf 1"))
root.AddChild(child1)

// 选择回调
tree.SetSelectedFunc(func(node *tview.TreeNode) {
    text := node.GetText()
    processNode(text)
})
```

### Python Textual

```python
from textual.widgets import Tree

tree = Tree("Root")
tree.root.expand()

# 添加节点
child1 = tree.root.add("Child 1", data={"type": "folder"})
child1.add_leaf("Leaf 1", data={"type": "file", "path": "/path"})

# 事件处理
@on(Tree.NodeSelected)
def on_node_selected(self, event: Tree.NodeSelected) -> None:
    node_data = event.node.data
    self.process_node(node_data)
```

---

## 📊 DataTable 对比

### Go tview

```go
table := tview.NewTable()
table.SetBorders(true)

// 设置表头
table.SetCell(0, 0, tview.NewTableCell("Name").SetTextColor(tcell.ColorYellow))
table.SetCell(0, 1, tview.NewTableCell("Value").SetTextColor(tcell.ColorYellow))

// 添加行
table.SetCell(1, 0, tview.NewTableCell("Item 1"))
table.SetCell(1, 1, tview.NewTableCell("Data 1"))
```

### Python Textual

```python
from textual.widgets import DataTable

table = DataTable()

# 添加列
table.add_column("Name", key="name")
table.add_column("Value", key="value")

# 添加行
table.add_row("Item 1", "Data 1", key="row1")
table.add_row("Item 2", "Data 2", key="row2")

# 更新单元格
table.update_cell("row1", "name", "Updated Item 1")
```

---

## 💬 Input 控件

### Go tview

```go
input := tview.NewInputField().
    SetLabel("Name: ").
    SetFieldWidth(30).
    SetAcceptanceFunc(tview.InputFieldInteger)  // 只接受整数

input.SetDoneFunc(func(key tcell.Key) {
    if key == tcell.KeyEnter {
        value := input.GetText()
        processInput(value)
    }
})
```

### Python Textual

```python
from textual.widgets import Input
from textual.validation import Number

# 创建输入框
input_widget = Input(
    placeholder="Enter number",
    validators=[Number(minimum=0, maximum=100)]
)

# 监听提交
@on(Input.Submitted)
def on_input_submitted(self, event: Input.Submitted) -> None:
    value = event.value
    self.process_input(value)

# 监听变化
@on(Input.Changed)
def on_input_changed(self, event: Input.Changed) -> None:
    # 实时验证
    if event.validation_result and event.validation_result.is_valid:
        self.show_success()
    else:
        self.show_error()
```

---

## 🎬 应用生命周期

### Go tview

```go
app := tview.NewApplication()

// 启动前设置
app.SetRoot(mainView, true)

// 运行（阻塞）
if err := app.Run(); err != nil {
    panic(err)
}

// 停止
app.Stop()
```

### Python Textual

```python
class MyApp(App):
    def on_mount(self) -> None:
        """应用启动后执行"""
        self.load_data()
        self.push_screen(MainScreen())

    async def on_ready(self) -> None:
        """UI 完全渲染后执行"""
        await self.animate_intro()

# 运行（同步或异步）
app = MyApp()
app.run()  # 阻塞模式

# 或
await app.run_async()  # 异步模式
```

---

## 🐛 调试技巧

### Go tview

```go
// 日志输出（写入文件）
logFile, _ := os.Create("debug.log")
defer logFile.Close()
log.SetOutput(logFile)

log.Printf("Current focus: %v", app.GetFocus())
```

### Python Textual

```python
# 方法1: textual console
# 在另一个终端运行：textual console

# 在代码中使用
self.log("Current screen:", self.screen)
self.log.debug("Debug info", extra={"data": obj})

# 方法2: textual run --dev
# 启动开发模式
# $ textual run --dev my_app.py

# 方法3: breakpoint
def on_button_pressed(self, event):
    breakpoint()  # 进入调试器
    self.process_action()
```

---

## 🚀 性能优化

### Go tview

```go
// 批量更新
app.QueueUpdateDraw(func() {
    list.Clear()
    for i := 0; i < 1000; i++ {
        list.AddItem(fmt.Sprintf("Item %d", i), "", 0, nil)
    }
})
```

### Python Textual

```python
# 批量更新
async def load_large_dataset(self):
    list_view = self.query_one(ListView)

    with self.batch_update():  # 延迟渲染
        list_view.clear()
        for i in range(1000):
            list_view.append(ListItem(f"Item {i}"))
    # 离开 with 块后一次性刷新

# DataTable 虚拟滚动（内置）
# 只渲染可见行，自动处理大数据集
table = DataTable()
for i in range(100000):
    table.add_row(f"Row {i}", f"Data {i}")
```

---

## 📚 常用组件速查

| 功能 | Go tview | Python Textual |
|-----|----------|---------------|
| 按钮 | `tview.Button` | `Button` |
| 复选框 | `tview.Checkbox` | `Checkbox` / `Switch` |
| 单选按钮 | `tview.RadioButtons` | `RadioSet` + `RadioButton` |
| 进度条 | - (需自定义) | `ProgressBar` |
| 加载动画 | - | `LoadingIndicator` |
| 标签页 | - (用 Pages) | `TabbedContent` + `TabPane` |
| 富文本 | `tview.TextView` + ANSI | `RichLog` (支持 Rich markup) |
| Markdown | - | `Markdown` |
| 代码高亮 | - | `Static` + `rich.syntax.Syntax` |

---

## 🔗 快速链接

- **Textual 官方文档**: https://textual.textualize.io/
- **Widget 库**: https://textual.textualize.io/widgets/
- **CSS 参考**: https://textual.textualize.io/styles/
- **示例代码**: https://github.com/Textualize/textual/tree/main/examples
- **Discord 社区**: https://discord.gg/Enf6Z3qhVr

---

**最后更新**: 2025-10-14
**维护者**: codex-feature agent
