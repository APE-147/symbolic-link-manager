## 最新需求（2025-10-18 Cycle 3：设置 lk 默认配置并移除 slm 命令）

**来源**：用户反馈

**需求描述**：
1. 将 `lk --data-root ~/Developer/Data --scan-roots ~/Developer/Cloud/Dropbox/-Code-` 设为默认配置
2. 用户运行 `lk` 时无需手动输入参数
3. 移除 `slm` 命令入口，仅保留 `lk`

**应用场景**：
- 用户每次运行都使用相同的路径，希望简化命令行输入
- 默认配置覆盖用户最常用的工作路径

**技术实现**：
- 修改 `src/slm/cli.py` 中的 `_parse_args()` 默认值
- 修改 `pyproject.toml` 移除 `slm` 入口点
- 保持 CLI 参数和配置文件覆盖能力
- 更新文档说明默认配置

**验收标准**：
- `lk` 命令默认使用 `~/Developer/Data` 作为 data-root
- `lk` 命令默认使用 `~/Developer/Cloud/Dropbox/-Code-` 作为 scan-roots
- `slm` 命令已移除（`which slm` 返回空）
- `lk` 无参数即可启动
- CLI 参数仍可覆盖默认值
- 所有测试通过

---

## 需求（2025-10-18 Cycle 2：路径解析修复）

**需求**：修复相对路径解析错误，使相对路径相对于 `data_root` 解析。

**问题场景**：
- 用户运行 `lk --data-root ~/Developer/Data --scan-roots ~/Developer/Cloud/Dropbox/-Code-`
- 选择目标后输入相对路径：`dev/desktop/plan/todo-event-database-data/hepta_sync-data`
- 遇到 `FileNotFoundError`，因为父目录不存在且路径被错误解析为相对于当前工作目录

**根本原因**：
- `cli.py:155` 中 `new_target.expanduser().resolve()` 将相对路径解析为相对于当前工作目录
- 用户期望：相对路径相对于 `~/Developer/Data`（data_root）
- 实际行为：相对路径相对于 `/Users/.../symbolic_link_changer`（cwd）

**技术要求**：
1. 在 `migrate_target_and_update_links()` 中添加 `data_root` 参数
2. 智能路径解析：相对路径 → 相对于 `data_root` 解析；绝对路径 → 保持不变
3. 在 `_safe_move_dir()` 中自动创建父目录（`new.parent.mkdir(parents=True, exist_ok=True)`）
4. 更新 `main()` 函数传递 `data_root` 参数
5. 添加相对路径解析测试用例
6. 更新文档说明路径解析规则

**验收标准**：
- 用户输入 `dev/new` → 解析为 `~/Developer/Data/dev/new`
- 绝对路径行为保持不变
- 自动创建不存在的父目录
- 所有现有测试通过 + 新增测试覆盖相对路径场景

---

## 需求（2025-10-18 Cycle 1：lk 命令别名）

**需求**：添加全局命令别名 `lk` 以更便捷地触发项目。

**应用场景**：
- 用户希望使用更短的命令 `lk` 来代替 `slm`，提升日常使用效率
- 两个命令（`lk` 和 `slm`）应具备完全相同的行为和参数
- 添加后向兼容性：现有 `slm` 命令必须保持正常工作

**技术要求**：
- 在 `pyproject.toml` 的 `[project.scripts]` 中添加 `lk = "slm.cli:main"`
- 确保安装后 `which lk` 能找到命令
- `lk --help` 和 `slm --help` 输出一致

---

## 原始需求（项目初始）

我需要当前项目, 通过 lk 命令全局触发


实现多级选单, 列出显示这个目录下(/Users/niceday/Developer/Data)
哪些文件夹是被其他符号链接指向的
- 点击进文件夹, 输入新的目标地址
  - 将当前的文件夹移动到新的目标地址
  - 检验对于新的目标地址, 原来的符号链接指向的位置是正确的

使用项目实现 https://github.com/tmbo/questionary