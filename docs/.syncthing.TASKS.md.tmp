# TASKS

> 首次由 PLAN.md 展开；后续自动更新/缩进新增子任务，严格遵循代办格式。

## Tasks for Cycle 1 (Based on PLAN.md Cycle 1 recommendations)

* [x] Task-1: 建立项目基础架构与文档基线 (Commit: bd9c95f)
  * 要求：创建符合 Python src 布局的项目结构；生成 pyproject.toml、README.md、CHANGELOG.md；建立 docs/ 文档完整性
  * 说明：按照 PLAN prompt 的 ⑤ 规范创建极简根目录与 src 布局；确保 REQUIRES/PLAN/TASKS/AGENTS 四件套完整
  * 测试命令：`ls -la && ls -la docs/ && ls -la src/`

* [x] Task-2: 实现符号链接扫描与发现模块 (Commit: 6fb9e41)
  * 要求：递归扫描 /Users/niceday/Developer/Cloud/Dropbox/-Code- 目录；识别所有符号链接；提取链接名称、路径、目标路径
  * 说明：使用 pathlib 与 os.path.islink；处理权限错误与循环链接；返回结构化数据（链接路径、目标路径、包含项目）
  * 测试命令：`python -m symlink_manager.core.scanner --scan-path /Users/niceday/Developer/Cloud/Dropbox/-Code-`

* [x] Task-3: 实现 Markdown 分类配置系统 (Commit: c2a8694)
  * 要求：定义 Markdown 配置文件格式（项目名称 + 符号链接路径列表）；实现解析器；支持分类与未分类链接区分
  * 说明：配置文件示例格式：`# Project-A\n- /path/to/link1\n- /path/to/link2`；解析为字典结构；未匹配项归入 unclassified
  * 测试命令：`python -m symlink_manager.core.classifier --config data/links_config.md`

* [x] Task-4: 实现交互式 TUI 界面 (Commit: d96b7ae)
  * 要求：使用 rich 或 prompt_toolkit 构建终端 UI；显示分类链接（已分类在顶部）；支持键盘导航与选择；按 Enter 进入详情
  * 说明：分类项显示项目名称作为分组；未分类项单独分组在底部；展示链接名称与当前目标路径
  * 测试命令：`lk` (调用全局命令进入交互界面)

* [x] Task-4.1: 修复 TUI 显示 UX 问题 - 主列表只显示链接名称 (Commit: ebcf493)
  * 要求：主列表显示仅 basename 而非完整路径；详情视图显示完整的 Symlink Location 和 Target Path；保持配色和分组方式
  * 说明：修改 `_render_list()` 使用 `os.path.basename(item.path)` 或 `item.name`；修改 `_render_detail()` 改进信息结构，使用 Panel 清晰标注 "Symlink Location" 和 "Target Path"
  * 测试命令：`pip install -e . && lk` (验证主列表只显示名称，按 Enter 后详情显示完整路径)
  * 证据：All tests pass (7/7); Changes committed in ebcf493

* [ ] Task-4.2: 实现 TUI 滚动视口与自适应列宽 (Critical UX Enhancement)
  * 要求：实现可滚动视口支持大列表（100+ 项）；自适应列宽匹配终端尺寸（80-200列）；显示滚动指示器；保持分组 header 可见性
  * 说明：添加 `_calculate_viewport_size()` 和 `_calculate_visible_range()` 函数；修改 `_render_list()` 只渲染可见行；实现自适应列宽（Name 30%, Status 10 chars, Target 剩余）；添加文本截断 `_truncate_text()`；显示 "↑ N more above" / "↓ N more below" 指示器
  * 测试命令：`./tests/create_test_symlinks.sh && lk --target /tmp/symlink_test_<timestamp>` (验证滚动流畅，指示器正确，不同终端宽度适配)
  * 证据：All existing tests pass (7/7); Package reinstalled; TUI_SCROLLING.md documentation created; Test script created

  * [x] Task-4.2.1: 修复 TUI 表格对齐严重错误 (CRITICAL BUG FIX) - Commit: (pending)
    * 要求：修复严重的对齐问题导致的对角线/锯齿状显示模式；每行必须在同一表格中对齐；所有列必须完美对齐
    * 说明：根本原因是每行创建独立的 Table 对象；解决方案是每组创建一个 Table，将所有行添加到该表，然后一次性打印；修改 `_render_list()` 引入 `current_table` 变量跟踪当前活动表格
    * 测试命令：`pytest tests/test_tui_alignment.py -v && lk --target /Users/niceday/Developer/Cloud/Dropbox/-Code-/Scripts` (验证所有行完美对齐，无对角线模式)
    * 证据：All 9 tests pass (7 original + 2 new alignment tests); Perfect alignment verified; Critical bug fixed

* [ ] Task-5: 实现目标路径查看与修改功能
  * 要求：选中链接后显示当前目标路径；提供输入框允许用户输入新目标路径；验证新路径有效性（父目录存在、无冲突）
  * 说明：使用 readlink 获取当前目标；新路径输入后进行预检查（父目录、权限、已存在文件/目录处理）
  * 测试命令：`python -m symlink_manager.services.link_updater --link-path /path/to/symlink --new-target /new/target`

* [ ] Task-6: 实现安全迁移与备份机制
  * 要求：迁移前创建备份（时间戳目录）；原子操作迁移文件/目录；失败时自动回滚；记录操作日志
  * 说明：备份到 data/backups/<timestamp>/；使用 shutil.move 或 os.rename；捕获异常并还原；所有操作写入 data/logs/migration.log
  * 测试命令：`python -m symlink_manager.services.migrator --source /old/target --dest /new/target --dry-run`

* [ ] Task-7: 实现全局 CLI 安装与入口点
  * 要求：配置 pyproject.toml 的 [project.scripts] 将 `lk` 命令映射到主入口；支持 pip install -e . 本地安装
  * 说明：entry point: `lk = symlink_manager.cli:main`；确保安装后可全局调用
  * 测试命令：`pip install -e . && lk --version && lk --help`

* [ ] Task-8: 实现测试套件与质量门
  * 要求：单元测试覆盖扫描、分类、迁移模块；集成测试覆盖端到端流程；使用 pytest + pytest-mock 模拟文件系统
  * 说明：测试用例包括：正常流程、权限错误、循环链接、目标冲突、备份恢复；目标覆盖率 ≥80%
  * 测试命令：`pytest tests/ -v --cov=src/symlink_manager --cov-report=term-missing`

