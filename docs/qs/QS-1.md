# QS-1 — slm / lk 决策记录（Cycle 0–3）

> Status: ✅ Locked decisions only（来源：docs/REQUIRES.md, docs/PLAN.md, AGENTS.md）；本文件于 2025-11-30 初始化，用于作为后续 PLAN/TASKS 的唯一决策输入。

---

## [#Q1] 项目初始：工具定位与基本能力

- 日期：2025-10-18（项目初始）
- 问题：本项目是否实现一个基于 Questionary 的 CLI 工具，通过 `lk` 命令全局触发，用于迁移 Data 根下被符号链接指向的目录？
- 结论：✅ 是。工具通过 `lk`（以及兼容的 `slm` 入口）运行，扫描配置的扫描根，找出目标位于 Data 根下的目录型符号链接，按目标目录分组并通过 Questionary 多级菜单完成：
  - 选择“被指向的目标目录”
  - 查看所有指向该目录的符号链接
  - 输入新的目标路径后生成迁移计划（默认 dry-run）
  - 确认后执行“移动目录→更新符号链接指向→结果校验”
- 来源：
  - docs/REQUIRES.md《原始需求（项目初始）》
  - docs/PLAN.md《Cycle 1 — 2025-10-18》Decision Questions #1–#3
  - AGENTS.md《功能概览（What it does）》

---

## [#Q2] Cycle 1：lk 命令别名

- 日期：2025-10-18（Cycle 1）
- 问题：是否添加全局命令别名 `lk`，并保证其行为与 `slm` 完全一致？
- 结论：✅ 是。通过在 `pyproject.toml` 的 `[project.scripts]` 中添加 `lk = "slm.cli:main"`，提供更短命令，保持与 `slm` 参数和行为一致，确保向后兼容。
- 来源：
  - docs/REQUIRES.md《需求（2025-10-18 Cycle 1：lk 命令别名）》
  - docs/PLAN.md《Cycle 1 — 2025-10-18》关于入口命令的设计讨论
  - AGENTS.md Run Log「[Feature: lk command alias]」

---

## [#Q3] Cycle 2：路径解析修复

- 日期：2025-10-18（Cycle 2）
- 问题：当用户输入相对路径作为新的目标目录时，应当相对于哪个基准路径解析？是否自动创建不存在的父目录？
- 结论：✅ 选择“相对于 data_root 解析，并自动创建父目录”。即：
  - 绝对路径保持不变；
  - `~` 开头的路径展开为用户主目录；
  - 其他相对路径一律相对于 `data_root` 解析；
  - 在迁移前，如果目标父目录不存在，自动 `mkdir -p` 创建。
- 来源：
  - docs/REQUIRES.md《需求（2025-10-18 Cycle 2：路径解析修复）》
  - docs/PLAN.md《Cycle 2 — 2025-10-18 (路径解析修复)》
  - AGENTS.md Run Log「[Fix: Relative path resolution]」

---

## [#Q4] Cycle 3：lk 默认配置与移除 slm 命令入口

- 日期：2025-10-18（Cycle 3）
- 问题：是否将常用的 data-root/scan-roots 作为 `lk` 的默认配置，并移除 `slm` 命令入口只保留 `lk`？
- 结论：✅ 是（决策已锁定，实施仍在进行中）。具体为：
  - `data-root` 默认值：`~/Developer/Data`
  - `scan-roots` 默认值：`["~/Developer/Cloud/Dropbox/-Code-"]`
  - 仅保留 `lk` 入口点，移除 `slm` 命令（用户仍可通过文档了解历史名称）
  - CLI 参数与配置文件继续覆盖默认值
- 实施状态：
  - 对应实现任务已记录于 docs/TASKS.md「Cycle 3 任务（2025-10-18）：设置 lk 默认配置并移除 slm 命令」
  - 目前部分任务仍为待办（未在代码中完全落地）
- 来源：
  - docs/REQUIRES.md《最新需求（2025-10-18 Cycle 3：设置 lk 默认配置并移除 slm 命令）》
  - docs/TASKS.md「Cycle 3 任务」章节
  - AGENTS.md Run Log「[Security: Privacy hardening & Git hygiene]」中的 lk/slm 配置上下文

---

## [#Q5] Cycle 1：迁移语义与冲突/备份策略

- 日期：2025-10-18（Cycle 1）
- 问题：数据目录迁移时采用何种语义（移动 vs 复制）以及如何处理目标已存在的冲突？
- 结论：✅ 采用“复制后切换符号链接、成功再删除旧目录”的安全策略，并在目标存在时：
  - 不直接覆盖；
  - 支持通过 Questionary 选择 Abort 或 Backup；
  - 备份策略为将既有目标重命名为 `dest~YYYYMMDD-HHMMSS`（冲突时追加 `-N`），再进行迁移。
- 来源：
  - docs/PLAN.md《Cycle 1 — 2025-10-18》Decision Questions #4–#5
  - AGENTS.md《重大缺陷与风险》《Run Log — [Codex Cycle 1]》关于 `_derive_backup_path()` 与 conflict_strategy 的描述
  - README.md / docs/USAGE_EXAMPLE.md「Conflict handling」「备份流程」示例

---

## [#Q6] Cycle 1：跨卷与原子性、校验与日志

- 日期：2025-10-18（Cycle 1）
- 问题：如何在尽量保证安全的前提下处理跨卷移动与近似原子性，并提供可审计的校验与日志？
- 结论：✅ 采用以下折中方案：
  - 迁移实现：优先使用 `Path.rename`，跨卷失败时回退到 `shutil.copytree` + `shutil.rmtree`；
  - 校验方式：使用“文件数/总字节数”的快速树摘要 `_fast_tree_summary()` 比较迁移前后；
  - 日志记录：提供可选 `--log-json`，以 JSON Lines 记录 preview/applied 阶段的 `move` / `retarget` / `backup` 事件，附带 Unix 时间戳。
- 来源：
  - docs/PLAN.md《Cycle 1 — 2025-10-18》Decision Questions #6–#7
  - AGENTS.md《实现思路》《重大缺陷与风险》关于原子性与校验粒度的记录
  - docs/TASKS.md「校验与日志」「JSON 操作日志与 --log-json 标志」任务条目

---

## [#Q7] Cycle 1：权限、忽略清单与范围限制

- 日期：2025-10-18（Cycle 1）
- 问题：在扫描和迁移过程中如何处理权限问题、忽略规则以及对象范围？
- 结论：✅ 当前版本采取保守策略：
  - 需要 sudo 时显式失败并给出提示，引导用户手工处理；
  - 不实现额外的忽略模式配置（如 `node_modules` / `.venv`），保持实现简单可预期；
  - 仅处理“目标位于 Data 根下的目录型符号链接”，不迁移普通目录或文件。
- 来源：
  - docs/PLAN.md《Cycle 1 — 2025-10-18》Decision Questions #8
  - AGENTS.md《功能概览（What it does）》对“目录型符号链接”的范围限定

