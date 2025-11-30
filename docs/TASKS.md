# TASKS

> 首次由 PLAN.md 展开；后续自动更新/缩进新增子任务，严格遵循代办格式。

- [x] 初始化 Python 项目与依赖（questionary 必选；rich/typer 可选）（来源：[#Q1]）
- [x] 实现“被指向的目标文件夹”发现器（扫描符号链接来源→目标在 Data 子树）（来源：[#Q1]）
- [x] 构建 Questionary 多级菜单（目标文件夹→来源符号链接→输入新目标路径）（来源：[#Q1]）
- [x] 迁移执行器（移动/跨卷复制回退→更新符号链接→最终验证）（来源：[#Q5], [#Q6]）
- [x] 校验与日志（dry-run、树摘要校验、JSON 操作日志与回滚脚本）（来源：[#Q6], [#Q7]）
  * 已实现 --log-json 标志用于 JSON Lines 日志记录
  * 已实现快速树摘要（文件计数+字节数，无哈希）
  * dry-run 阶段显示当前和新目标的摘要
  * 执行后显示最终目标的摘要
  - [x] JSON 操作日志与 `--log-json` 标志（追加 JSON Lines，含 phase/type/from/to/link/ts）
- [x] 冲突与权限处理（目标存在策略、忽略清单、仅目录型符号链接）（来源：[#Q5], [#Q7]）
  * 要求：检测目标已存在，提供 Abort/Backup 选项
  * 说明：实现 `_derive_backup_path()` 生成带时间戳的备份路径（格式：`dir~YYYYMMDD-HHMMSS`）
  * 测试命令：创建已存在的目标目录，运行 slm 并选择备份策略
  * 证据：2025-10-18 codex cycle 1 完成（commit pending）
- [x] CLI 与配置（扫描根参数/配置文件、默认值）（来源：[#Q1], docs/REQUIRES.md）
  * 支持 `~/.config/slm.yml`（PyYAML），CLI 参数优先级最高
  * 读取配置后打印加载路径，默认回退至 `~/Developer/Data` 与 `~`
- [x] 测试最小集（模拟数据集与烟雾测试）（来源：AGENTS.md Run Log「[Codex Cycle 3]」）
  * 要求：至少 3 个单元测试，1 个集成测试
  * 说明：测试 backup path 生成、冲突处理、备份迁移、完整 dry-run→apply 流程
  * 测试命令：`pytest tests/` — 全部通过 (4 个测试)
  * 证据：2025-10-18 codex cycle 3（创建 tests/test_cli.py，100% 通过率）
- [x] 文档与示例（README、更新 REQUIRES 与使用说明）（来源：AGENTS.md Run Log「[Codex Cycle 4]」）
  * README.md 增补冲突策略、日志格式、配置载入提示
  * docs/USAGE_EXAMPLE.md 对齐 JSON 时间戳格式、备份流程、进度 100%
- [x] 修复相对路径解析错误（Cycle 2，2025-10-18）（来源：[#Q3]）
  * 要求：相对路径相对于 data_root 解析；自动创建父目录
  * 说明：
    - migrate_target_and_update_links() 添加 data_root 参数与智能路径解析
    - _safe_move_dir() 自动创建父目录（mkdir parents=True）
    - main() 传递 data_root 到迁移函数
  * 测试命令：`pytest tests/` — 6/6 通过（新增 2 个测试）
  * 证据：
    - 提交：bc9f030
    - 分支：fix/relative-path-resolution
    - 新测试：test_migrate_with_relative_path_resolved_against_data_root, test_safe_move_dir_creates_parent_directories
    - 文档：README.md L47-53（路径解析规则）, docs/USAGE_EXAMPLE.md L90-94（相对路径示例）

---

## Cycle 3 任务（2025-10-18）：设置 lk 默认配置并移除 slm 命令

- [ ] 修改 pyproject.toml 移除 slm 命令入口（来源：[#Q4]）
  * 要求：移除 `slm = "slm.cli:main"` 行，仅保留 `lk` 入口
  * 说明：简化命令入口，避免混淆
  * 测试命令：`pip install -e . && which slm`（应返回空）

- [ ] 修改 src/slm/cli.py 设置默认参数（来源：[#Q4]）
  * 要求：在 _parse_args() 中设置 data-root 和 scan-roots 默认值；更新 prog 参数为 "lk"
  * 说明：
    - data-root 默认值：`"~/Developer/Data"`
    - scan-roots 默认值：`["~/Developer/Cloud/Dropbox/-Code-"]`
    - prog 参数从 "slm" 改为 "lk"
  * 测试命令：`lk --help`（查看默认值说明）

- [ ] 更新测试文件 tests/test_cli.py（来源：[#Q4]）
  * 要求：新增测试用例验证默认参数值
  * 说明：测试 _parse_args([]) 返回的默认值是否正确
  * 测试命令：`pytest tests/test_cli.py::test_parse_args_defaults -v`

- [ ] 运行完整测试套件（来源：[#Q4]）
  * 要求：所有测试通过
  * 说明：确保变更未破坏现有功能
  * 测试命令：`pytest tests/ -v`

- [ ] 更新文档（README.md, docs/USAGE_EXAMPLE.md）（来源：[#Q4]）
  * 要求：说明默认配置；移除 slm 命令引用
  * 说明：
    - README.md 添加"默认配置"章节
    - docs/USAGE_EXAMPLE.md 更新示例为 `lk` 命令
    - 说明 CLI 参数和配置文件可覆盖默认值
  * 测试命令：手动检查文档完整性

- [ ] 更新 AGENTS.md（来源：[#Q4]）
  * 要求：更新项目快照、Run Log、TODO 状态
  * 说明：记录本次实施的变更摘要和证据
  * 测试命令：检查 AGENTS.md 一致性
