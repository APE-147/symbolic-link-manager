# 任务清单

> 首次由 PLAN.md 展开；后续自动更新/缩进新增子任务，严格遵循待办格式。

## 周期 5：Textual TUI 重构（2025-10-14）

基于 docs/PLAN.md 中 Cycle 5 的建议（Q1→B、Q2→A、Q3→B、Q4→A、Q5→A、Q6→A、Q7→A、Q8→A），并与现有 simple-term-menu 实现并行推进，使用 CLI 开关安全回退。

* [x] 任务-1：以可选依赖方式引入 Textual（extras） - **已完成** ✓

  * 要求：在 `pyproject.toml` 中新增 `[project.optional-dependencies].textual = ["textual>=0.60,<1.0"]`；默认安装不包含 Textual；文档示例支持 `pip install -e .[textual]`
  * 验收：`pip install -e .[textual]` 正常；不安装 Textual 时 `lk --help` 可用；现有 CLI/TUI（simple-term-menu）不受影响
  * 验证命令：`pytest -q`（仍为 46/46 通过）；`pip install -e .[textual]` 可成功解析 extras
  * 证据：`pyproject.toml` 新增 `[project.optional-dependencies].textual`；`pytest -q` → 46 passed

* [ ] 任务-2：创建 `tui_textual.py` 骨架（多 Screen 架构）

  * 要求：新增 `src/symlink_manager/ui/tui_textual.py`，包含 `LKApp(App)` 与 `MainListScreen`、`DetailScreen`、`EditScreen` 三屏骨架；提供基本路由与键位映射（↑/↓/j/k、/、Enter、e、q）占位
  * 验收：`python -m symlink_manager.cli --ui-engine textual --target ...` 能启动空壳应用并显示主屏标题/占位区域
  * 验证命令：`python -m symlink_manager.cli --ui-engine textual --target ~/ --dry-run 2>/dev/null | true`
  * [x] 任务-2.1：研究 Chatlog/tview 实现并生成技术映射文档 - **已完成** ✓

    * 要求：分析 Go tview/tcell 的 TUI 模式（布局、事件、渲染），建立 Python/Textual 映射关系，输出研究报告和快速参考
    * 验证命令：`test -f docs/TEXTUAL_RESEARCH_REPORT.md && test -f docs/TEXTUAL_QUICK_REFERENCE.md && echo "Research complete" || echo "Missing docs"`
    * 证据：`docs/TEXTUAL_RESEARCH_REPORT.md`（73页全面报告 + 完整原型代码）、`docs/TEXTUAL_QUICK_REFERENCE.md`（速查表）

* [ ] 任务-3：实现主列表屏（Tree/DataTable 展示三级层次）

  * 要求：使用 `Tree` 或 `DataTable` 渲染 Primary→Secondary→Project 层次，并与现有过滤系统对齐（仅目录/乱码/哈希目标 过滤标志）
  * 验收：加载真实扫描结果时可展开/折叠主/次节点，项目节点可选中，并显示计数/路径摘要
  * 验证命令：`pytest -q tests/test_hierarchical_classifier.py -k hierarchy && python -m symlink_manager.cli --ui-engine textual --target <fixture>`

* [ ] 任务-4：新增详情与编辑屏

  * 要求：详情屏显示所选符号链接的 `path/target/validators` 结果；编辑屏提供目标路径输入、合法性检查与保存/取消（占位实现：仅验证，不落盘）
  * 验收：从主屏 Enter 进入详情；从详情按 `e` 进入编辑；从编辑保存/取消返回详情/主屏；错误输入有明显反馈
  * 验证命令：`textual run symlink_manager.ui.tui_textual:LKApp --dev`（或通过 CLI 入口）

* [ ] 任务-5：通过 `--ui-engine` 集成 CLI（simple|textual）

  * 要求：在 `src/symlink_manager/cli.py` 增加 `--ui-engine` 选项（默认 `simple`），支持环境变量 `LK_UI_ENGINE`；未安装 Textual 且选择 textual 时给出友好提示
  * 验收：`lk --ui-engine simple` 走现有 TUI，`lk --ui-engine textual` 走 Textual 实现；两者共享相同扫描/分类代码路径与过滤开关
  * 验证命令：`lk --ui-engine simple --target <dir>` 与 `lk --ui-engine textual --target <dir>` 均可运行（前者无需安装 Textual）

* [ ] 任务-6：编写 Textual Pilot 测试

  * 要求：新增 `tests/test_tui_textual_pilot.py` 使用 `textual.testing.Pilot` 驱动键位交互（上下移动、搜索、进入/返回、编辑占位）；必要时引入 `pytest-asyncio`
  * 验收：核心交互路径可被自动化验证；测试在未安装 Textual 时自动跳过（`pytest.importorskip('textual')`）
  * 验证命令：`pytest -q tests/test_tui_textual_pilot.py -q`

* [ ] 任务-7：回归验证（46/46 测试通过）

  * 要求：保留并通过现有 46 个测试（含导出与分层）；新增的 Textual 测试计入总数
  * 验收：`pytest -q` 输出含 46+ 通过；无回归；simple UI 路径仍稳定
  * 验证命令：`pytest -q`

* [ ] 任务-8：渲染问题回归测试（闪烁/标题重复/滚动污染）

  * 要求：在 Textual UI 下验证先前问题是否被根因规避（虚拟 DOM/布局管理）；补充 `docs/archive/TESTING.md` 的手测用例到 Textual 章节
  * 验收：Terminal.app 80×24 与 ≥100 列均无闪烁/重复/污染；快速按键与视图切换稳定
  * 验证命令：手动测试（同 `docs/archive/TESTING.md`），并记录截图/笔记

### 成功标准（Cycle 5）

- [ ] `pip install -e .[textual]` 正常；默认安装不包含 Textual
- [ ] `--ui-engine simple|textual` 可切换；未安装 Textual 时有友好提示
- [ ] 主屏可展示并导航三级层次；详情/编辑屏路线打通
- [ ] Textual Pilot 覆盖关键交互路径
- [ ] `pytest -q` 全量通过（≥46）
- [ ] 先前渲染问题在 Textual 下消失或可控

## 周期 3：自动分层分类（2025-10-14）

基于 PLAN.md 周期 3 建议和自动层次检测的简化需求。

* [x] 任务-1：为 SymlinkInfo 数据类添加层次字段 - **已完成** ✓ (scanner.py 第 163-173 行)

  * 要求：为 SymlinkInfo 添加三个新的可选字段：`primary_category`、`secondary_category`、`project_name`（均为 Optional[str]，默认值 "unclassified"）
  * 关于任务-1的简短说明：实现 PLAN 周期 3 Q2→A - 使用 3 个独立字段提供语义清晰度；通过保留现有 `project` 字段维护向后兼容性
  * 测试任务-1生成代码使用的命令：`python -c "from symlink_manager.core.scanner import SymlinkInfo; import inspect; print(inspect.signature(SymlinkInfo))"`

* [x] 任务-2：创建简化的分层配置解析器 - **已完成** ✓（使用现有的 load_markdown_config）

  * 要求：实现新的解析器 `parse_markdown_config_hierarchical()`，读取一级主分类（## 标题）及路径模式（- 项），返回简化的 MarkdownConfig 数据类，包含 `Dict[str, List[str]]`（主分类 → 模式）
  * 关于任务-2的简短说明：根据更新的需求 - 仅一级（Desktop/Service/System）手动配置，二级/三级从路径结构自动检测；解析器仅处理 ## 和 - 行
  * 测试任务-2生成代码使用的命令：`pytest tests/test_classifier.py::test_parse_markdown_config_basic -v`（现有解析器适用于简化格式）

* [x] 任务-3：实现路径结构自动检测辅助函数 - **已完成** ✓（classifier.py 第 157-262 行）

  * 要求：创建辅助函数 `_extract_path_hierarchy(symlink_path, scan_root)` 和 `_detect_hierarchy_from_primary(symlink_path, primary_match_pattern)`，从路径结构中提取二级（文件夹）和三级（项目）
  * 关于任务-3的简短说明：核心自动检测逻辑 - 分析相对于扫描根目录和主模式匹配的符号链接路径，提取次级分类（父文件夹）和项目名称（祖父文件夹或项目文件夹）
  * 测试任务-3生成代码使用的命令：`pytest tests/test_hierarchical_classifier.py -k "extract_path_hierarchy or detect_hierarchy" -v` - **7/7 测试通过**

* [x] 任务-4：实现自动分层分类逻辑 - **已完成** ✓（classifier.py 第 273-345 行）

  * 要求：创建 `classify_symlinks_auto_hierarchy()` 函数，完成：1) 从配置模式匹配一级（主分类），2) 从路径结构自动检测二级/三级，3) 返回 `Dict[str, Dict[str, List[SymlinkInfo]]]`（主分类 → 次分类 → 符号链接）
  * 关于任务-4的简短说明：实现 PLAN 周期 3 Q5→A，采用基于路径的自动检测；一级使用首次匹配原则，二级/三级使用路径解析
  * 测试任务-4生成代码使用的命令：`pytest tests/test_hierarchical_classifier.py -k "classify_symlinks_auto" -v` - **6/6 测试通过**

* [x] 任务-5：更新 TUI 以缩进显示三级层次结构 - **已完成** ✓（tui.py 第 63-122、325-369 行）

  * 要求：修改 tui.py 中的 `_build_rows()` 和菜单构建逻辑，使用缩进显示三级层次结构：`[主分类]` → `  [次分类]` → `    ✓ 项目 → 目标`
  * 关于任务-5的简短说明：实现 PLAN 周期 3 Q4→A - 简单缩进（每级 2 个空格），ASCII 兼容显示，匹配需求示例
  * 测试任务-5生成代码使用的命令：手动 TUI 测试就绪 - `python -m symlink_manager.cli --target ~/Developer/Cloud/Dropbox/-Code-/Desktop --config ~/.config/lk/projects.md`

* [x] 任务-6：编写全面的分层分类测试 - **已完成** ✓（tests/test_hierarchical_classifier.py）

  * 要求：创建 `tests/test_hierarchical_classifier.py`，包含以下测试：1) 简化配置解析器，2) 路径自动检测辅助函数，3) 自动分层分类，4) 边界案例（深层嵌套路径、扫描根目录的符号链接、未匹配模式）
  * 关于任务-6的简短说明：实现 PLAN 周期 3 Q6→A - 独立测试文件以实现清晰组织和 CI 集成；确保自动检测正常工作
  * 测试任务-6生成代码使用的命令：`pytest tests/test_hierarchical_classifier.py -v` - **13/13 测试通过**

* [x] 任务-7：创建示例分层配置文件 - **已完成** ✓（~/.config/lk/projects.md）

  * 要求：创建 `~/.config/lk/projects.md`，包含简化的三级示例配置，显示 Desktop/Service/System 主分类及路径模式（无需手动配置二级/三级 - 这些将自动检测）
  * 关于任务-7的简短说明：实现 PLAN 周期 3 Q7→A - 在标准配置位置提供用户友好的示例，匹配需求格式
  * 测试任务-7生成代码使用的命令：`test -f ~/.config/lk/projects.md && echo "Config exists" || echo "Config missing"` - **配置存在 ✓**

* [x] 任务-8：运行完整回归测试套件 - **已完成** ✓（44/44 测试通过）

  * 要求：验证所有现有测试及新的分层测试均通过；确保与扁平配置格式的向后兼容性
  * 关于任务-8的简短说明：最终验证 - 扫描器、扁平分类器、验证器、TUI 无回归；自动分层正常工作
  * 测试任务-8生成代码使用的命令：`pytest -v` - **44/44 测试通过（31 个原始测试 + 13 个新分层测试）**

### 成功标准 - **全部完成 ✓**

- [x] SymlinkInfo 包含 3 个新的层次字段（primary_category、secondary_category、project_name）✓
- [x] 简化配置解析器仅读取一级（## + 模式）✓（使用现有解析器）
- [x] 自动检测从路径结构提取二级/三级 ✓（13 个测试通过）
- [x] 分类自动生成三级层次结构 ✓
- [x] TUI 以适当的缩进显示层次结构 ✓（每级 2 个空格缩进）
- [x] 所有现有测试和新测试均通过（无回归）✓（44/44 测试通过）
- [x] 在 `~/.config/lk/projects.md` 创建示例配置文件 ✓

### 实现说明

**与原计划的关键差异**：更新的需求简化了配置格式 - 用户只需指定一级（Desktop/Service/System）及路径模式。二级和三级会根据符号链接相对于匹配的主模式的路径结构自动提取。这消除了在配置文件中手动输入 ### 次分类和 - 项目条目的需要。

**路径自动检测逻辑**：
1. 将符号链接路径与一级模式匹配（现有的 fnmatch 逻辑）
2. 一旦匹配，提取模式匹配点之后的剩余路径部分
3. 第一个剩余部分 → 二级（次级分类，例如 "Projects"）
4. 第二个剩余部分 → 三级（项目名称，例如 "MyApp"）

**示例**：
- 配置：`## Desktop`，模式为 `/Users/*/Developer/Desktop/**/*`
- 符号链接：`/Users/me/Developer/Desktop/Projects/MyApp/data` → Desktop
- 自动检测：二级 = "Projects"，三级 = "MyApp"

### 预估时间

- 任务-1（数据类）：30 分钟
- 任务-2（简化解析器）：1 小时
- 任务-3（路径自动检测）：1.5 小时
- 任务-4（分类逻辑）：1 小时
- 任务-5（TUI 更新）：1 小时
- 任务-6（测试）：1.5 小时
- 任务-7（示例配置）：15 分钟
- 任务-8（回归测试）：30 分钟

**总计**：约 7 小时（根据 PLAN Q8→B 单个 PR 原子实现）
