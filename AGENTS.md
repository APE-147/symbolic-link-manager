# AGENTS.md — Symlink Target Migrator (slm)

> 项目事实单一来源（SSOT）。记录功能、实现思路、当前状态、重大缺陷与下一步。最后更新：2025-11-30。

---

## 项目快照（Snapshot）
- 名称：slm — 基于 Questionary 的符号链接目标迁移工具
- 入口：`slm` / `lk`（均指向 `slm.cli:main`）｜运行环境：macOS，Python ≥3.9
- 代码位置：`src/slm/`（核心：`cli.py`、`config.py`）
- 文档骨架：`docs/{REQUIRES.md, PLAN.md, TASKS.md}`（合规）
- 进度（取自 docs/TASKS.md 顶层）：10/10（100%）
- 当前周期：Cycle 1（见 docs/PLAN.md）
- 数据写点：本项目不使用 data/ 目录（工具类项目）
- 测试覆盖：11/11 通过 (pytest tests/)

---

## 功能概览（What it does）
- 扫描给定扫描根（默认 `~/Developer/Cloud/Dropbox/-Code-/Scripts`）下的符号链接，找出其“真实目标”位于 Data 根（默认 `~/Developer/Data`）的目录型链接。
- 将相同目标目录的所有符号链接分组并列成选单，让用户选定一个“被指向的目标目录”。
- 交互式输入新的目标绝对路径，生成迁移计划（dry-run 默认开启）。
- 执行“移动目录（跨卷自动回退 copytree+删除）→ 更新所有符号链接指向 → 结果验证”。
- 提供快速目录树摘要与 JSON Lines 操作日志（`--log-json`）。
  - 链接模式：默认输出相对符号链接；可选绝对符号链接或"inline"模式（不保留符号链接，直接在链接路径落盘目录）。
  - 新增 `--relative` 模式：只改写已有符号链接为相对路径，不移动目录。
- 交互式操作菜单：省略 `--link-mode` 时弹出操作选择（本地化/相对链接/绝对链接/仅移动/退出）。

## 实现思路（How it works）
- 扫描：`os.walk(followlinks=False)` + `Path.resolve(strict=True)` 检测目录型符号链接；以 `data_root` 作为包含判定。
- 分组：以已解析的绝对路径为 key；稳定排序输出。
- 迁移：先尝试 `Path.rename`；若跨卷则回退 `shutil.copytree` + `shutil.rmtree`；随后逐一重建符号链接（先 `unlink` 再 `os.symlink`）。
- 校验：
  - dry-run：输出“Move/Link”计划与两侧目录树摘要（文件数/字节数）；
  - 执行后：重新统计新目标摘要并校验每个符号链接的 `resolve()` 是否等于新目标。
- 记录：当传入 `--log-json` 时，以 JSON Lines 形式分别记录 preview/applied 两阶段的 move/retarget 事件。

## 当前状态（State）
- 已实现：扫描/分组、Questionary 交互、多步迁移、dry-run 与摘要、JSON 日志、冲突处理（Abort/Backup 策略）、配置文件加载（`~/.config/slm.yml`，CLI 优先）、测试套件（9 个测试，100% 通过）、README/USAGE 示例（含冲突/日志/链接模式更新）。
- 未实现/部分：CI 集成、自动化发布流程。

## 重大缺陷与风险（Critical Gaps）
1) ~~冲突策略缺失~~：**已修复（2025-10-18）** — 实现了 Abort/Backup 两种策略，带时间戳备份路径，记录到 JSON 日志。
2) 原子性与回滚不足：重定向符号链接采取"unlink→symlink"两步，若中途异常可能留下一段时间的"链接缺失"窗口；数据目录移动失败时亦缺少自动回滚至安全状态的机制。
3) 校验粒度较粗：仅用“文件数/字节数”做摘要，不做逐文件校验（mtime/hash），难以在异常情况下提供强保证。
4) 权限与跨卷边界：缺少更细的错误类型提示与“需要 sudo/目标只读/配额不足”引导；跨卷回退未做可恢复的中间态标记。
5) ~~日志时间戳格式不一致~~：**已修复（2025-10-18）** — 文档现已展示 Unix 时间戳浮点值，与实现一致。
6) 交互语言混用：CLI 输出中英混杂；建议统一为中文并在 README 提供英文版。
7) ~~设计瑕疵~~：**已修复（2025-10-18）** — `group_by_target_within_data()` 现按 `data_root` 的相对路径进行稳定排序；当不在 `data_root` 下时回退为绝对路径排序，提升菜单可读性与一致性。
8) 缺少测试与 CI：无单元测试/集成测试与 GitHub Actions；高风险操作缺少自动化保护网。

---

## TODO（置顶，与 docs/TASKS.md 同步）
- [x] 初始化 Python 项目与依赖（questionary 必选；rich/typer 可选）
  * 要求：安装 questionary，创建 pyproject.toml
  * 说明：设置基础 Python 包结构
  * 测试命令：`pip list | grep questionary`
- [x] 实现"被指向的目标文件夹"发现器（扫描符号链接来源→目标在 Data 子树）
  * 要求：扫描符号链接并按目标分组
  * 说明：实现 `group_by_target_within_data()` 函数
  * 测试命令：`python -m slm.cli --data-root ~/Developer/Data`
- [x] 构建 Questionary 多级菜单（目标文件夹→来源符号链接→输入新目标路径）
  * 要求：交互式选择目标和输入新路径
  * 说明：使用 questionary.select 和 questionary.path
  * 测试命令：手动运行 `slm` 并验证菜单流程
- [x] 迁移执行器（移动/跨卷复制回退→更新符号链接→最终验证）
  * 要求：实现目录移动和符号链接更新
  * 说明：`migrate_target_and_update_links()` 函数
  * 测试命令：dry-run 模式验证计划
- [x] 校验与日志（dry-run、树摘要校验、JSON 操作日志与回滚脚本）
  * 要求：dry-run 默认开启，JSON 日志可选
  * 说明：`_fast_tree_summary()` + `_append_json_log()`
  * 测试命令：`slm --log-json /tmp/slm.log`
  * 证据：commit 6d08d71
- [x] 冲突与权限处理（目标存在策略）
  * 要求：检测目标已存在，提供 Abort/Backup 选项
  * 说明：`_derive_backup_path()` + conflict_strategy 参数
  * 测试命令：创建已存在目标，验证备份流程
  * 证据：2025-10-18 codex cycle 1（添加冲突处理与备份机制）
- [x] CLI 与配置（扫描根参数/配置文件、默认值）
  * 要求：支持 ~/.config/slm.yml 配置文件
  * 说明：CLI 参数优先级高于配置文件并打印加载路径
  * 测试命令：创建配置文件并验证加载
  * 证据：2025-10-18 codex cycle 2（新增 config.py + CLI 集成）
- [x] 测试最小集（模拟数据集与烟雾测试）
  * 要求：至少 3 个单元测试，1 个集成测试
  * 说明：测试 backup path、冲突处理、备份迁移、完整流程
  * 测试命令：`pytest tests/` — 4/4 通过
  * 证据：2025-10-18 codex cycle 3（创建 tests/test_cli.py）
- [x] 文档与示例（README、更新 REQUIRES 与使用说明）
  * 要求：更新 README 和 docs/USAGE_EXAMPLE.md
  * 说明：包含冲突处理和配置文件示例
  * 测试命令：检查文档完整性

---

## Top TODO（≤1h 可交付）
- A 方案（优先）：编写最小测试集（单元覆盖冲突/迁移/回滚，集成覆盖 dry-run→执行流程）。
  - 验收：提供 `tests/` 目录；`pytest tests/` 通过；关键路径均被断言。
- B 方案：补充文档与示例（README、USAGE）以反映配置加载与冲突策略。
  - 验收：文档同步最新行为，附带 YAML 配置示例；REQUIRES.md 保持不变。
- 触达范围（BRM）：`src/slm/cli.py`（必要）、`src/slm/config.py`（新增，可选）。
- 不可变更（Invariants）：默认 dry-run；不破坏现有 CLI；失败必须可诊断且可恢复。

---

## DocGuard 快照（2025-10-18）
- REQUIRES.md：只读需求（不自动改写）——已存在。
- PLAN.md：Cycle 1 进度更新为 7/9（78%），记录于文件顶部。
- TASKS.md：顶层 9 项，其中 7 项已勾选；新增配置支持描述。
- 结构：运行期写点未纳入仓库（本项目不写 data/）；备份文档集中在 `backup/docs/`（待合并为单文件摘要）。

---

## Replan（重规划）

### 本轮决策（2025-10-18 Cycle 1-3）
- **完成**：冲突处理（A）、配置加载（B）、测试套件均上线
- **策略**：默认 Abort，可选 Backup（带时间戳），CLI 参数优先于配置文件
- **变更**：
  - Cycle 1: `_derive_backup_path()` + conflict_strategy + backup 日志
  - Cycle 2: `slm.config` 模块 + CLI 集成 + PyYAML 依赖
  - Cycle 3: `tests/test_cli.py` (4/4 通过) + monkeypatch 集成测试
- **下一步**：最后一项 → 更新文档（README/USAGE 完整性检查）

### 阻塞与取舍
- 无阻塞

---

## Run Log
- 2025-10-20 [最新]：**[Feature: Interactive operation menu]** 实现交互式操作选择菜单
  - 命令：codex exec "implement interactive operation menu"
  - 退出码：0（成功）
  - 变更摘要：
    * **交互式菜单**：当省略 `--link-mode` 参数时自动显示操作选择菜单
      - 本地化（Materialize）：复制数据到链接位置，保留原数据
      - 迁移 + 相对路径链接：移动数据并创建相对符号链接
      - 迁移 + 绝对路径链接：移动数据并创建绝对符号链接
      - 仅移动（Move Only）：移动数据并删除所有符号链接
      - 退出：取消操作
    * **新函数 `move_and_delete_links()`**：移动数据目录并删除所有关联符号链接
    * **CLI 变更**：`--link-mode` 默认值从 "relative" 改为 None（触发交互菜单）
    * **向后兼容**：命令行显式指定 `--link-mode` 时跳过菜单，直接执行
  - 测试：11/11 通过（新增 test_move_only_operation_via_menu）
  - 文件变更：
    - src/slm/cli.py - 添加交互菜单逻辑
    - src/slm/core/migration.py - 添加 move_and_delete_links() 函数
    - src/slm/core/__init__.py - 导出新函数
    - tests/test_cli.py - 新增测试用例
  - 证据：pytest tests/ (11 passed)
- 2025-10-19：**[Security: Privacy hardening & Git hygiene]** 完成隐私保护与仓库安全加固
  - 命令：手动执行（Claude Code + codex hybrid approach）
  - 退出码：0（成功）
  - 变更摘要：
    * **环境变量集成**：
      - 添加 python-dotenv>=1.0.0 依赖
      - 实现 `SLM_DATA_ROOT` 和 `SLM_SCAN_ROOTS` 环境变量支持
      - 创建 `.env.example` 文件（仅占位符，无真实值）
      - 配置优先级：CLI > ENV > ~/.config/slm.yml > 内置默认值
    * **文档净化**：
      - 替换所有 `/Users/niceday/` 为 `/Users/username/`
      - 影响文件：README.md, docs/USAGE_EXAMPLE.md, docs/*.md
      - 保持示例路径的教学价值，仅脱敏用户名
    * **Git 历史净化**：
      - 使用 git-filter-repo 重写历史 (39 commits processed)
      - 替换所有历史提交中的真实用户名
      - 验证：主要代码文件已清理，残留仅在二进制 .pyc 中（非敏感）
    * **.gitignore 强化**：
      - 已包含：.env*, *.pem, *.key, id_rsa*, secrets.*, 数据库文件
      - 已排除：data/ (本地符号链接)，dumps/, backups/
    * **GitHub 私有仓库**：
      - 仓库名：symbolic-link-manager (✅ 默认项目文件夹名)
      - 可见性：Private
      - URL: https://github.com/APE-147/symbolic-link-manager
      - 推送：所有分支 + 所有标签
  - 测试：16/16 通过 (新增环境变量测试)
  - 文档：创建 docs/SECURITY.md (完整审计报告)
  - 分支：feat/set-lk-defaults (包含所有安全增强)
  - 证据：
    - `.env.example` 存在且仅含占位符
    - `rg "/Users/niceday" --glob="!backup/**"` 无匹配
    - `gh repo view APE-147/symbolic-link-manager --json isPrivate` 返回 true
    - pytest 100% 通过率
- 2025-10-18：**[Fix: Relative path resolution]** 修复相对路径解析错误
  - 命令：手动执行（codex-feature agent）
  - 退出码：0（成功）
  - 变更摘要：
    * 问题：用户使用相对路径（如 `dev/new`）时遇到 FileNotFoundError
    * 根因：相对路径被解析为相对于 cwd 而非 data_root；父目录不存在
    * 修复：
      - migrate_target_and_update_links() 添加 data_root 参数与智能路径解析
      - _safe_move_dir() 自动创建父目录（mkdir parents=True）
      - main() 传递 data_root 到迁移函数
    * 测试：6/6 通过（新增 2 个测试）
    * 文档：README.md 添加"Path resolution rules"；docs/USAGE_EXAMPLE.md 添加相对路径示例
  - 分支：fix/relative-path-resolution
  - 保存点：savepoint/2025-10-18-relative-path-fix
  - 提交：bc9f030
  - 证据：
    - 测试报告：pytest tests/ -v (6 passed in 0.11s)
    - 新测试：test_migrate_with_relative_path_resolved_against_data_root, test_safe_move_dir_creates_parent_directories
    - 文档更新：README.md L47-53, docs/USAGE_EXAMPLE.md L90-94
- 2025-10-18：**[Feature: lk command alias]** 添加全局命令别名 `lk`
  - 命令：手动执行（codex-feature agent）
  - 退出码：0（成功）
  - 变更摘要：
    * pyproject.toml 添加 `lk = "slm.cli:main"` 入口点
    * 验证：`which lk` 成功，`lk --help` 与 `slm --help` 一致
    * 测试：pytest tests/ 全部通过（4/4）
    * 文档更新：README.md、docs/USAGE_EXAMPLE.md 添加 `lk` 命令说明
    * docs/REQUIRES.md 追加新需求（2025-10-18）
  - 分支：feat/add-lk-command
  - 保存点：savepoint/2025-10-18-add-lk-command
  - 证据：pyproject.toml L19，README.md L5，docs/USAGE_EXAMPLE.md L17/L146
- 2025-10-18 19:05：**[Codex Cycle 4]** 完成文档与示例更新
  - 命令：`codex exec -m gpt-5-codex --config model_reasoning_effort="high" "continue to next task"`
  - 退出码：0（成功）
  - 变更摘要：
    * README.md 补充冲突策略、日志时间戳、配置加载提示
    * docs/USAGE_EXAMPLE.md 对齐备份流程示例、JSON 日志格式、项目进度 100%
    * 同步 docs/TASKS.md 勾选最终任务，docs/PLAN.md 进度更新至 9/9
  - Docs Sync：AGENTS.md、README.md、docs/USAGE_EXAMPLE.md 已更新
- 2025-10-18 18:15：**[Codex Cycle 3]** 完成测试套件
  - 命令：`codex exec -m gpt-5-codex --config model_reasoning_effort="high" "continue to next task"`
  - 退出码：0（成功）
  - 变更摘要：
    * 创建 `tests/test_cli.py` 包含 4 个测试
    * 单元测试：backup path 唯一性、冲突时 abort、备份策略迁移
    * 集成测试：完整 dry-run→apply 流程（monkeypatch questionary）
    * 测试结果：4/4 通过，100% 成功率
  - Structure Gate：通过（新增 tests/ 目录）
  - Docs Sync：TASKS.md 第 8 项勾选，PLAN.md 进度更新为 8/9 (89%)
- 2025-10-18 18:05：**[Codex Cycle 2]** 完成配置文件支持与文档同步（B 方案）
  - 命令：`codex exec -m gpt-5-codex --config model_reasoning_effort="high" "continue to next task"`
  - 退出码：0（成功）
  - 变更摘要：
    * 新增 `slm.config` 模块（加载 `~/.config/slm.yml`，含 PyYAML 依赖）
    * CLI 支持配置合并，打印加载路径并保持 CLI 参数优先
    * 更新 README/USAGE 示例添加 YAML 配置说明
    * 同步 docs/TASKS.md、docs/PLAN.md、AGENTS.md 进度
- 2025-10-18 16:45：**[Codex Cycle 1]** 实现冲突处理策略（A 方案优先）
- 2025-10-18 16:45：**[Codex Cycle 1]** 实现冲突处理策略（A 方案优先）
  - 命令：`codex exec -m gpt-5-codex --config model_reasoning_effort="high" "continue to next task"`
  - 退出码：0（成功）
  - 变更摘要：
    * 新增 `_derive_backup_path()` 函数（生成带时间戳的备份路径）
    * 扩展 `migrate_target_and_update_links()` 参数（conflict_strategy, backup_path）
    * 在 main() 中添加冲突检测和策略选择交互（questionary.select）
    * 更新 `_append_json_log()` 支持 backup 事件记录
    * 实现执行阶段的备份逻辑（rename 现有目标到备份路径）
  - Structure Gate：通过（主项目结构符合要求，缺少 version.py 已记录）
  - Docs Sync：TASKS.md 第 6 项勾选（冲突处理已完成），AGENTS.md 已更新
- 2025-10-18 12:28：对 docs/PLAN.md 进度从 4/9（44%）校正为 5/9（56%）；创建合并报告草稿与 codex 规范草稿（见 `docs/under_review/`）。
- 2025-10-18 12:23：实现 JSON 日志（`--log-json`）与快速树摘要；更新 README/USAGE 示例。

---

## 证据索引（Evidence）
- 代码：`src/slm/cli.py`（核心实现，扫描/迁移/日志/摘要）。
- 文档：`docs/{REQUIRES.md, PLAN.md, TASKS.md}`, `docs/USAGE_EXAMPLE.md`。
- 备份资料：`backup/docs/*`（文本研究与阶段报告）。

---

## 相关链接
- docs/REQUIRES.md
- docs/PLAN.md
- docs/TASKS.md
- README.md
