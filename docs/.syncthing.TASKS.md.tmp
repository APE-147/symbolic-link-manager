# TASKS

> 首次由 PLAN.md 展开；后续自动更新/缩进新增子任务，严格遵循代办格式。

## Tasks for Cycle 1 (Based on PLAN.md Cycle 1 recommendations)

* [ ] Task-1: 建立项目基础架构与文档基线
  * 要求：创建符合 Python src 布局的项目结构；生成 pyproject.toml、README.md、CHANGELOG.md；建立 docs/ 文档完整性
  * 说明：按照 PLAN prompt 的 ⑤ 规范创建极简根目录与 src 布局；确保 REQUIRES/PLAN/TASKS/AGENTS 四件套完整
  * 测试命令：`ls -la && ls -la docs/ && ls -la src/`

* [ ] Task-2: 实现符号链接扫描与发现模块
  * 要求：递归扫描 /Users/niceday/Developer/Cloud/Dropbox/-Code- 目录；识别所有符号链接；提取链接名称、路径、目标路径
  * 说明：使用 pathlib 与 os.path.islink；处理权限错误与循环链接；返回结构化数据（链接路径、目标路径、包含项目）
  * 测试命令：`python -m symlink_manager.core.scanner --scan-path /Users/niceday/Developer/Cloud/Dropbox/-Code-`

* [ ] Task-3: 实现 Markdown 分类配置系统
  * 要求：定义 Markdown 配置文件格式（项目名称 + 符号链接路径列表）；实现解析器；支持分类与未分类链接区分
  * 说明：配置文件示例格式：`# Project-A\n- /path/to/link1\n- /path/to/link2`；解析为字典结构；未匹配项归入 unclassified
  * 测试命令：`python -m symlink_manager.core.classifier --config data/links_config.md`

* [ ] Task-4: 实现交互式 TUI 界面
  * 要求：使用 rich 或 prompt_toolkit 构建终端 UI；显示分类链接（已分类在顶部）；支持键盘导航与选择；按 Enter 进入详情
  * 说明：分类项显示项目名称作为分组；未分类项单独分组在底部；展示链接名称与当前目标路径
  * 测试命令：`link` (调用全局命令进入交互界面)

* [ ] Task-5: 实现目标路径查看与修改功能
  * 要求：选中链接后显示当前目标路径；提供输入框允许用户输入新目标路径；验证新路径有效性（父目录存在、无冲突）
  * 说明：使用 readlink 获取当前目标；新路径输入后进行预检查（父目录、权限、已存在文件/目录处理）
  * 测试命令：`python -m symlink_manager.services.link_updater --link-path /path/to/symlink --new-target /new/target`

* [ ] Task-6: 实现安全迁移与备份机制
  * 要求：迁移前创建备份（时间戳目录）；原子操作迁移文件/目录；失败时自动回滚；记录操作日志
  * 说明：备份到 data/backups/<timestamp>/；使用 shutil.move 或 os.rename；捕获异常并还原；所有操作写入 data/logs/migration.log
  * 测试命令：`python -m symlink_manager.services.migrator --source /old/target --dest /new/target --dry-run`

* [ ] Task-7: 实现全局 CLI 安装与入口点
  * 要求：配置 pyproject.toml 的 [project.scripts] 将 `link` 命令映射到主入口；支持 pip install -e . 本地安装
  * 说明：entry point: `link = symlink_manager.cli:main`；确保安装后可全局调用
  * 测试命令：`pip install -e . && link --version && link --help`

* [ ] Task-8: 实现测试套件与质量门
  * 要求：单元测试覆盖扫描、分类、迁移模块；集成测试覆盖端到端流程；使用 pytest + pytest-mock 模拟文件系统
  * 说明：测试用例包括：正常流程、权限错误、循环链接、目标冲突、备份恢复；目标覆盖率 ≥80%
  * 测试命令：`pytest tests/ -v --cov=src/symlink_manager --cov-report=term-missing`

