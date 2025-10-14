# 任务清单

> 首次由 PLAN.md 展开；后续自动更新/缩进新增子任务，严格遵循待办格式。

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
