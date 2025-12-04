# QS-2 — slm / lk 决策记录（Cycle 4：repo-sign 集成）

> Generated: 2025-12-04 | Questions: #Q8 - #Q18 | Status: Active
> 本文件记录 Cycle 4 的项目级 API 与 repo-sign 集成相关决策。

---

## Progress

- `total_decisions_needed`: 15
- `answered`: 11
- `progress_pct`: 73%
- Visual: [███████░░░] 73%

---

## Decisions

### [#Q8] Cycle 4：任务优先级

**Status**: ✅ Locked     **Category**: Planning
**Question**: 应该先完成 Cycle 3（移除 slm 命令、设置 lk 默认值）再开发新功能，还是直接合并实现？
**Options**:
A. **先完成 Cycle 3** - 先清理技术债（~30分钟），让 lk 命令稳定后再扩展架构
B. **合并实现** - 一次性重构，避免两次修改 CLI，但复杂度和风险更高
C. **跳过 Cycle 3** - 保留 slm/lk 双入口，直接开发项目级 API
**Answer**: A - 先完成 Cycle 3
**Rationale**: 保持原子性变更，降低风险，确保 lk 命令稳定后再进行架构扩展

---

### [#Q9] Cycle 4：新模块位置

**Status**: ✅ Locked     **Category**: Architecture
**Question**: 新模块 project_mode.py 应该放在哪个位置？
**Options**:
A. **src/slm/core/** - 与 scanner.py、migration.py 同级，作为核心功能
B. **src/slm/services/** - 作为高层服务，调用 core 模块
C. **src/slm/project/** - 创建独立子包，便于未来扩展项目级功能
**Answer**: A - src/slm/core/
**Rationale**: 与现有核心模块保持一致的组织结构，便于复用 scanner/migration 功能

---

### [#Q10] Cycle 4：CLI 框架选择

**Status**: ✅ Locked     **Category**: Architecture
**Question**: CLI 框架选择：继续使用 argparse 还是迁移到 Typer（repo-sign 使用 Typer）？
**Options**:
A. **保持 argparse** - 最小变更，通过 add_subparsers 实现子命令
B. **迁移到 Typer** - 与 repo-sign 统一，原生支持子命令，代码更简洁
C. **混合方案** - 现有功能保持 argparse，新功能用单独的 Typer 入口
**Answer**: B - 迁移到 Typer
**Rationale**: 与 repo-sign 保持技术栈统一，Typer 原生支持子命令和自动帮助生成，长期维护更简单

---

### [#Q11] Cycle 4：API 设计风格

**Status**: ✅ Locked     **Category**: API Design
**Question**: API 设计风格：函数式还是类封装？
**Options**:
A. **纯函数式** - get_project_data_status(root, settings)，简单直接
B. **类封装** - ProjectManager(settings).get_status(root)，状态可复用
C. **混合** - 数据类型用 dataclass，操作用函数
**Answer**: C - 混合
**Rationale**: 结合两者优点：dataclass 提供类型安全和清晰的数据模型，函数式 API 保持简单易用

---

### [#Q12] Cycle 4：shared_with 字段实现方式

**Status**: ✅ Locked     **Category**: Implementation
**Question**: shared_with 字段（其它项目也指向同一 data 目录）如何实现？
**Options**:
A. **调用时扫描** - 每次调用 get_status 时扫描所有 scan_roots，完整但较慢
B. **调用方传入** - 调用方传入 all_project_roots 列表，灵活但需调用方维护
C. **延迟加载** - 初始为空，提供单独的 find_shared_projects() 函数
**Answer**: B - 调用方传入
**Rationale**: repo-sign 已维护项目列表，避免重复扫描，调用方有更完整的上下文

---

### [#Q13] Cycle 4：Typer 迁移策略

**Status**: ✅ Locked     **Category**: Migration
**Question**: Typer 迁移策略：如何处理现有的交互式菜单流程？
**Options**:
A. **完整迁移** - 现有交互式流程也迁移到 Typer，作为默认子命令或 callback
B. **保留双入口** - lk 保持现有 argparse 流程，新增 lk-project 使用 Typer
C. **渐进式** - 新功能用 Typer，旧功能暂不迁移，未来逐步统一
**Answer**: A - 完整迁移
**Rationale**: 一次性完成迁移，避免维护两套 CLI 框架，长期维护成本更低

---

### [#Q14] Cycle 4：repo-sign 集成方式

**Status**: ✅ Locked     **Category**: Integration
**Question**: repo-sign 集成方式偏好？
**Options**:
A. **Python 库调用** - from slm.core.project_mode import get_project_data_status，直接快速
B. **CLI 调用** - subprocess.run(['lk', 'status', '--json'])，解耦但较慢
C. **两者都支持** - 库 API + CLI 都提供，让调用方选择
**Answer**: C - 两者都支持
**Rationale**: 灵活性最高，repo-sign 可选择最适合的方式，CLI 也便于脚本和调试

---

### [#Q15] Cycle 4：data 目录名称配置

**Status**: ✅ Locked     **Category**: Configuration
**Question**: data 目录名称配置：是否允许自定义（如 .data, _data）？
**Options**:
A. **固定为 data** - 简单统一，不支持自定义
B. **可配置** - SlmSettings.data_dir_name 支持自定义，默认 data
**Answer**: A - 固定为 data
**Rationale**: 保持简单，与 repo-sign 的 newproj.sh 约定一致，避免过度配置化

---

### [#Q16] Cycle 4：Commit 策略

**Status**: ✅ Locked     **Category**: Process
**Question**: Cycle 3 完成后是否需要单独提交（commit）还是等新功能一起？
**Options**:
A. **单独提交** - Cycle 3 完成后立即 commit，保持原子性变更
B. **一起提交** - 等新功能完成后统一 commit，减少提交数量
C. **用户决定** - 完成各阶段后询问用户是否提交
**Answer**: A - 单独提交
**Rationale**: 原子性变更便于回滚和审计，Cycle 3 是独立的清理任务

---

### [#Q17] Cycle 4：CLI 子命令命名风格

**Status**: ✅ Locked     **Category**: CLI Design
**Question**: 新的 CLI 子命令命名风格偏好？
**Options**:
A. **lk project status** - 类似 git 风格，空格分隔子命令
B. **lk proj-status** - 短单词 + 连字符，更简洁
C. **lk status** - 最简短，与现有交互式流程平级
**Answer**: C - lk status
**Rationale**: 最简短易记，status 明确表达查看状态的意图

---

### [#Q18] Cycle 4：API 版本兼容性

**Status**: ✅ Locked     **Category**: Maintenance
**Question**: 是否需要为 repo-sign 集成添加版本兼容性保证（如稳定 API 版本号）？
**Options**:
A. **不需要** - 两个项目同一作者维护，直接追踪最新即可
B. **简单版本号** - 添加 __version__ 和 CHANGELOG，不做严格兼容性承诺
**Answer**: A - 不需要
**Rationale**: 两个项目由同一作者维护，可以同步更新，避免过度工程化

---

## Summary - 实施计划

### Phase 1: Cycle 3 完成（独立 commit）
1. 修改 `pyproject.toml` 移除 `slm` 入口点
2. 修改 `src/slm/cli.py` 设置默认参数并更新 `prog="lk"`
3. 更新测试和文档
4. **单独提交**

### Phase 2: Typer 迁移
1. 添加 `typer` 依赖到 `pyproject.toml`
2. 重构 `cli.py` 为 Typer 应用
3. 保持现有交互式流程作为默认命令
4. 验证所有现有功能正常

### Phase 3: 项目级 API 实现
1. 创建 `src/slm/core/project_mode.py`
2. 实现 `ProjectDataStatus` dataclass
3. 实现 `get_project_data_status()` 和 `set_project_data_mode()` 函数
4. 添加 `lk status` 子命令（支持 `--project-root` 和 `--json`）

### Phase 4: 集成与文档
1. 导出新 API 到 `slm.core.__init__.py`
2. 更新 README 和 USAGE_EXAMPLE
3. 添加单元测试
4. 更新 AGENTS.md Run Log

---

## 来源

- 用户交互问答：2025-12-04
- 参考文档：docs/REQUIRES.md, docs/PLAN.md, AGENTS.md
- 关联项目：repo-sign (/Users/niceday/Developer/Cloud/Dropbox/-Code-/Scripts/service/manager/repo-sign)
