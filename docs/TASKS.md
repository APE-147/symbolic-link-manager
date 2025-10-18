# TASKS

> 首次由 PLAN.md 展开；后续自动更新/缩进新增子任务，严格遵循代办格式。

- [x] 初始化 Python 项目与依赖（questionary 必选；rich/typer 可选）
- [x] 实现“被指向的目标文件夹”发现器（扫描符号链接来源→目标在 Data 子树）
- [x] 构建 Questionary 多级菜单（目标文件夹→来源符号链接→输入新目标路径）
- [x] 迁移执行器（移动/跨卷复制回退→更新符号链接→最终验证）
- [x] 校验与日志（dry-run、树摘要校验、JSON 操作日志与回滚脚本）
  * 已实现 --log-json 标志用于 JSON Lines 日志记录
  * 已实现快速树摘要（文件计数+字节数，无哈希）
  * dry-run 阶段显示当前和新目标的摘要
  * 执行后显示最终目标的摘要
  - [x] JSON 操作日志与 `--log-json` 标志（追加 JSON Lines，含 phase/type/from/to/link/ts）
- [x] 冲突与权限处理（目标存在策略、忽略清单、仅目录型符号链接）
  * 要求：检测目标已存在，提供 Abort/Backup 选项
  * 说明：实现 `_derive_backup_path()` 生成带时间戳的备份路径（格式：`dir~YYYYMMDD-HHMMSS`）
  * 测试命令：创建已存在的目标目录，运行 slm 并选择备份策略
  * 证据：2025-10-18 codex cycle 1 完成（commit pending）
- [x] CLI 与配置（扫描根参数/配置文件、默认值）
  * 支持 `~/.config/slm.yml`（PyYAML），CLI 参数优先级最高
  * 读取配置后打印加载路径，默认回退至 `~/Developer/Data` 与 `~`
- [x] 测试最小集（模拟数据集与烟雾测试）
  * 要求：至少 3 个单元测试，1 个集成测试
  * 说明：测试 backup path 生成、冲突处理、备份迁移、完整 dry-run→apply 流程
  * 测试命令：`pytest tests/` — 全部通过 (4 个测试)
  * 证据：2025-10-18 codex cycle 3（创建 tests/test_cli.py，100% 通过率）
- [x] 文档与示例（README、更新 REQUIRES 与使用说明）
  * README.md 增补冲突策略、日志格式、配置载入提示
  * USAGE_EXAMPLE.md 对齐 JSON 时间戳格式、备份流程、进度 100%
