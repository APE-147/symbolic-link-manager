# Textual TUI 迁移 - 执行摘要

> **快速概览** - 5 分钟了解从 simple-term-menu 到 Textual 的迁移方案
>
> **日期**: 2025-10-14
> **状态**: 研究完成 ✅ | 实施准备就绪

---

## 🎯 核心问题

**当前 TUI 存在的问题**：
- ✅ 闪烁（已通过 `console.screen()` 缓解）
- ✅ 标题重复（已通过手动 Rich header 修复）
- ❌ **根本问题未解决**：simple-term-menu 架构限制
  - 缺乏虚拟 DOM 和状态管理
  - 依赖手动 `console.clear()` 和 ANSI 序列
  - 不适合复杂布局和多视图导航

---

## ✅ 推荐方案

### Textual - Python 原生现代 TUI 框架

**核心优势**：
1. **虚拟 DOM** - 智能 diff 渲染，自动避免闪烁
2. **声明式布局** - CSS 驱动，类似 Web 开发
3. **Rich 集成** - 同一作者（Will McGugan），无缝兼容
4. **AsyncIO 事件循环** - 类似 Go tcell，性能优异
5. **活跃维护** - 2024 年仍在积极开发

**技术映射**（Go tview → Python Textual）：
- `tview.Application` → `textual.app.App`
- `tview.Flex` → `Horizontal` / `Vertical`
- `tview.Tree` → `Tree`
- `SetInputCapture()` → `on_key()` / `BINDINGS`
- 手动 `Draw()` → 自动虚拟 DOM

---

## 📋 实施路线图

### Phase 1: 基础设施（1.5h）
- **任务-1** ✅: 引入 Textual 依赖（optional）
- **任务-2**: 创建骨架应用（3 个 Screen）

### Phase 2: 核心功能（4.5h）
- **任务-3**: 主列表（Tree 三层级）
- **任务-4**: 详情 + 编辑屏

### Phase 3: 集成与验证（4.25h）
- **任务-5**: CLI 集成（`--ui-engine` 开关）
- **任务-6**: Textual Pilot 自动化测试
- **任务-7**: 回归测试（46/46）
- **任务-8**: 渲染问题验证

**总时间**: ~10.25 小时（2-3 天，每天 3-4h）

---

## 🎨 新架构预览

```
LKApp (主应用)
├── MainListScreen (主屏幕)
│   ├── Header (标题栏 - 自动布局)
│   ├── Tree (三层级可折叠树)
│   │   ├── [PRIMARY] Desktop
│   │   │   ├── [SECONDARY] Projects
│   │   │   │   └── MyApp → /target
│   │   └── [PRIMARY] Service
│   ├── PreviewPanel (可选宽屏)
│   └── Footer (快捷键提示)
├── DetailScreen (详情 - 独立 Screen)
└── EditScreen (编辑 - 独立 Screen)
```

**关键改进**：
- 无需手动 `console.clear()`
- 虚拟 DOM 自动处理渲染
- CSS 响应式布局（自适应终端尺寸）
- 声明式事件绑定（`BINDINGS` / `@on`）

---

## 💡 核心技术亮点

### 1. 虚拟 DOM 渲染
```python
# 自动批量更新，无闪烁
widget.update("new content")
widget.styles.background = "blue"
# ↑ 内部自动 diff + 最小变更刷新
```

### 2. CSS 驱动布局
```python
CSS = """
#main {
    layout: grid;
    grid-size: 2 1;
    grid-columns: 1fr 2fr;
}
"""
# ↑ 类似 Web，熟悉且强大
```

### 3. Screen 导航
```python
self.push_screen(DetailScreen(item))  # 进入
self.pop_screen()                     # 返回
# ↑ 类似移动 App，清晰的视图栈
```

### 4. 响应式属性
```python
item_count = reactive(0)

def watch_item_count(self, old, new):
    self.border_title = f"Items ({new})"

self.item_count += 1  # 自动触发更新
# ↑ 类似 React，声明式状态管理
```

---

## 📊 风险评估

| 风险 | 影响 | 缓解措施 |
|-----|------|---------|
| 学习曲线 | 中 | 提供完整原型代码 + 速查表 |
| 迁移不完整 | 高 | 保留 simple UI 作为回退 |
| 终端兼容性 | 低 | Textual 支持主流终端 |

**关键缓解点**：
- ✅ CLI 开关（`--ui-engine simple|textual`）
- ✅ optional-dependencies（不强制安装）
- ✅ 渐进迁移（只读功能先行）

---

## 📚 交付物

### 已完成 ✅
1. **研究报告**（1071 行）
   - 📄 `docs/TEXTUAL_RESEARCH_REPORT.md`
   - 包含：技术分析、架构设计、完整原型代码
   - 时间估算：10.25 小时

2. **快速参考**（634 行）
   - 📄 `docs/TEXTUAL_QUICK_REFERENCE.md`
   - 包含：Go/Python 对照表、常用模式、速查代码片段

3. **原型代码**（完整可运行）
   - 📄 研究报告附录 A
   - 包含：LKApp、3 个 Screen、Tree 组件

### 待实施
- [ ] 任务-2: 骨架应用（基于原型改进）
- [ ] 任务-3: 主列表实现
- [ ] 任务-4: 详情 + 编辑
- [ ] 任务-5: CLI 集成
- [ ] 任务-6-8: 测试与验证

---

## 🚀 快速开始（下一步）

### 1. 安装 Textual
```bash
pip install -e .[textual]
```

### 2. 创建骨架文件
```bash
# 复制研究报告附录 A 的原型代码到：
# src/symlink_manager/ui/tui_textual.py
```

### 3. 测试运行
```bash
python -m symlink_manager.cli --ui-engine textual --target ~/
```

### 4. 参考文档
- **详细设计**: `docs/TEXTUAL_RESEARCH_REPORT.md`
- **代码速查**: `docs/TEXTUAL_QUICK_REFERENCE.md`
- **官方文档**: https://textual.textualize.io/

---

## 🎯 成功标准

### 功能验收
- [ ] 主列表显示三层级（可折叠）
- [ ] 键盘导航流畅（↑/↓/j/k/Enter/Esc/q）
- [ ] 搜索功能（/）
- [ ] 详情视图完整
- [ ] 编辑视图带验证

### 质量验收
- [ ] **无闪烁**（连续导航 50 次）
- [ ] **无标题重复**
- [ ] **无滚动污染**
- [ ] 所有测试通过（≥46）

---

## 🔍 关键洞察

### 为什么 Textual 能解决渲染问题？

1. **虚拟 DOM**
   - simple-menu: 每次重绘整屏 → 闪烁
   - Textual: Diff 算法 → 只更新变化区域

2. **状态管理**
   - simple-menu: 无状态，依赖手动清屏
   - Textual: 响应式属性 → 自动跟踪变化

3. **布局引擎**
   - simple-menu: 手动计算行列 → 容易错位
   - Textual: CSS Grid/Flex → 声明式，自动计算

4. **事件系统**
   - simple-menu: 同步阻塞 → 按键卡顿
   - Textual: AsyncIO → 非阻塞，流畅响应

---

## 📞 支持资源

- **Textual Discord**: https://discord.gg/Enf6Z3qhVr
- **示例项目**: https://github.com/Textualize/textual/tree/main/examples
- **作者 Twitter**: @willmcgugan

---

**版本**: 1.0
**作者**: codex-feature agent
**日期**: 2025-10-14
**状态**: 研究完成 ✅ | 准备实施 🚀
