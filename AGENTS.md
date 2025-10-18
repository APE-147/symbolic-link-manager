# AGENTS.md — Symlink Target Migrator (slm)

> Central, living project doc. Single place to see status, plan, and next actions. Updated on 2025-10-18.

---

## Header / Project Snapshot
- Project: slm — Questionary-based symlink target migrator
- Owner: Codex CLI agent
- Date: 2025-10-18
- Environment: macOS, Python ≥3.9
- Entry point: `slm` (`slm.cli:main`)
- Progress (from docs/TASKS.md): 5/9 = 56%
- Current Cycle: Cycle 1 (docs/PLAN.md)

---

## Definitions (FWU / BRM / Invariants / Touch Budget / FF)
- FWU (Feature Work Unit): Smallest end-to-end valuable change that can be delivered in ≤1 day.
- BRM (Blast Radius Map): Enumerates modules/files likely impacted by the FWU.
- Invariants: Non-negotiable contracts that must hold after changes (APIs, UX promises, safety rules).
- Touch Budget: Explicit allow/deny list of files that can be modified for this FWU.
- FF (Feature Flag): Runtime toggle or kill switch guarding the FWU (N/A unless stated).

---

## Checklist Mirror (from docs/TASKS.md)

- [x] 初始化 Python 项目与依赖（questionary 必选；rich/typer 可选）
- [x] 实现"被指向的目标文件夹"发现器（扫描符号链接来源→目标在 Data 子树）
- [x] 构建 Questionary 多级菜单（目标文件夹→来源符号链接→输入新目标路径）
- [x] 迁移执行器（移动/跨卷复制回退→更新符号链接→最终验证）
- [x] 校验与日志（dry-run、树摘要校验、JSON 操作日志与回滚脚本）
- [ ] 冲突与权限处理（目标存在策略、忽略清单、仅目录型符号链接）
- [ ] CLI 与配置（扫描根参数/配置文件、默认值）
- [ ] 测试最小集（模拟数据集与烟雾测试）
- [ ] 文档与示例（README、更新 REQUIRES 与使用说明）

---

## Top TODO (≤1h)
✅ COMPLETED: JSON logging and tree summary

Next priority: Conflict/permission handling or configuration file support.

- Scope: Add conflict resolution when target exists, OR add YAML config file support (~/.config/slm.yml).
- Options:
  A. Conflict handling: When new target exists, offer abort (default), backup-and-move, or force-overwrite.
  B. Config file: Support reading scan-roots and data-root from YAML; CLI args take precedence.
- Acceptance (Option A):
  - Test scenario where new target already exists; verify abort behavior and optional backup.
- Acceptance (Option B):
  - Create ~/.config/slm.yml with scan_roots/data_root; verify values loaded; CLI overrides work.
- BRM: `src/slm/cli.py` (and potentially `src/slm/config.py` for Option B).
- Invariants: Default behavior unchanged; dry-run safety preserved; backward compatibility.
- Touch Budget: ALLOWED `src/slm/cli.py`, `src/slm/config.py` (new); FORBIDDEN others.
- FF: Not required (opt-in features).

---

## Run Log
- 2025-10-18 12:23: Implemented JSON logging (--log-json flag) and fast tree summary. Updated progress to 5/9 (56%).
  - Added `_fast_tree_summary()` function using os.scandir
  - Integrated summaries into dry-run preview and post-apply output
  - JSON Lines format for operation logs (preview/applied phases)
  - Tested with temporary directory structure
- 2025-10-18 12:21: Scaffolded AGENTS.md (this file) with snapshot, definitions, Top TODO, run log, replan, evidence index, and links. Synced PLAN progress to 4/9 (44%).
- 2025-10-18: Implemented `--log-json` JSON Lines logging (preview/applied phases) and updated README usage with jq example.

---

## Replan
- No blockers detected. Next action is Top TODO (≤1h): document `--log-json` with a jq validation snippet in README.

---

## Evidence Index
- Code: `src/slm/cli.py` - Core implementation (350+ lines)
- Tests: Manual testing with `/tmp/slm_test` structure
- Logs: JSON Lines format implemented and verified
- Docs: `USAGE_EXAMPLE.md` - Comprehensive usage guide
- Commit: 7da33f1 "feat(slm): Implement questionary-based symlink target migration system"
- Updated: `src/slm/cli.py` (added `--log-json`, JSON Lines writer)
- Updated: `README.md` (documented `--log-json`)

---

## Links
- docs/REQUIRES.md
- docs/PLAN.md
- docs/TASKS.md
- README.md
