# slm 使用示例

## 快速开始

### 1. 安装

```bash
cd /Users/niceday/Developer/Cloud/Dropbox/-Code-/Scripts/system/data-storage/symbolic_link_changer
pip install -e .
```

### 2. 基本使用

#### 交互式选单（默认 dry-run + 结果确认）

```bash
slm  # 或使用更短的别名: lk
```

默认行为：
- Data root: `~/Developer/Data`
- Scan roots: `~` （用户主目录，可通过配置或 CLI 覆盖）
- Dry-run: 开启。CLI 会先展示迁移计划并在 `执行上述操作吗？` 时再次确认。

#### 自定义扫描范围

```bash
slm --data-root ~/Developer/Data --scan-roots ~ ~/Projects ~/Documents
```

#### 带 JSON 日志

```bash
slm --log-json ./migration.jsonl
```

查看 JSON 日志：
```bash
jq . migration.jsonl
```

#### 使用配置文件设置默认值

在 `~/.config/slm.yml` 中声明默认的 Data root 与扫描范围（需要 PyYAML）：

```yaml
data_root: /Users/niceday/Developer/Data
scan_roots:
  - /Users/niceday
  - /Users/niceday/Developer
```

当配置文件被加载时，CLI 会输出 `已加载配置文件：<绝对路径>`，以便追踪默认来源。CLI 参数始终优先于配置文件。

## 使用场景示例

### 场景 1：整理开发项目的 Data 目录

**背景**：你在 `~/Developer/Data` 下有多个项目的数据文件夹，其他位置的符号链接指向这些文件夹。

**步骤**：

1. 启动工具：
```bash
slm --data-root ~/Developer/Data --scan-roots ~ ~/Developer
```

2. 工具会扫描并显示所有被符号链接指向的文件夹，例如：
```
选择一个被指向的目标文件夹:
> myproject-data  (2 个链接)
  another-project-data  (1 个链接)
  退出
```

3. 选择要移动的文件夹，工具会显示所有指向它的符号链接：
```
以下符号链接指向该目录:
- /Users/niceday/workspace/myproject/data
- /Users/niceday/Documents/backup/myproject-link
```

4. 输入新的目标路径（支持 tab 自动补全）：
```
输入新的目标绝对路径: /Users/niceday/Developer/Data/archived/myproject-data
```

5. 如果新目标已存在，CLI 会提示冲突策略：
```
目标路径已存在：/Users/niceday/Developer/Data/archived/myproject-data
选择冲突处理策略：
  ◯ 中止（默认，保持现状）
  ◉ 备份后迁移（先重命名为 archived/myproject-data~20251018-193011）
  ◯ 强制覆盖（不支持）
```
选择“备份后迁移”会在执行前把既有目录重命名为 `dest~YYYYMMDD-HHMMSS`（若冲突再追加 `-N`）。

6. 确认 dry-run 计划：
```
计划 (dry-run):
  • Backup: /Users/niceday/Developer/Data/archived/myproject-data -> /Users/niceday/Developer/Data/archived/myproject-data~20251018-193011
  • Move: /Users/niceday/Developer/Data/myproject-data -> /Users/niceday/Developer/Data/archived/myproject-data
  • Link: /Users/niceday/workspace/myproject/data -> /Users/niceday/Developer/Data/archived/myproject-data
  • Link: /Users/niceday/Documents/backup/myproject-link -> /Users/niceday/Developer/Data/archived/myproject-data
summary(current=files:42 bytes:1048576, new=files:12 bytes:4096)
执行上述操作吗？ (y/N):
```

7. 确认后执行，工具会：
   - 根据冲突策略备份（如选择）
   - 移动目录到新位置（跨卷自动回退到 copytree + 删除）
   - 更新所有符号链接指向新位置
   - 验证符号链接（`Path.resolve(strict=True)` 必须指向新目标）
   - 显示最终摘要 `summary(new=files:… bytes:…)`

### 场景 2：使用 JSON 日志跟踪操作

```bash
slm --log-json ./slm-operations.jsonl
```

查看操作记录：
```bash
# 查看所有操作
jq . ./slm-operations.jsonl

# 仅查看 preview 阶段
jq 'select(.phase == "preview")' ./slm-operations.jsonl

# 仅查看实际执行的移动操作
jq 'select(.phase == "applied" and .type == "move")' ./slm-operations.jsonl
```

JSON 日志格式示例（`ts` 为 Unix 时间戳浮点数）：
```json
{"phase": "preview", "type": "backup", "from": "/path/new", "to": "/path/new~20251018-120001", "ts": 1734559201.123}
{"phase": "preview", "type": "move", "from": "/path/old", "to": "/path/new", "ts": 1734559201.123}
{"phase": "preview", "type": "retarget", "link": "/workspace/link1", "to": "/path/new", "ts": 1734559201.123}
{"phase": "applied", "type": "move", "from": "/path/old", "to": "/path/new", "ts": 1734559234.987}
{"phase": "applied", "type": "retarget", "link": "/workspace/link1", "to": "/path/new", "ts": 1734559234.987}
```

## 命令行选项

```
slm [选项]   # 或使用别名: lk [选项]

选项:
  --data-root PATH       Data 目录的根路径（默认: ~/Developer/Data）
  --scan-roots PATH ...  扫描符号链接的根目录列表（默认: ~）
  --dry-run              仅预览迁移计划（默认开启，用于兼容旧脚本）
  --log-json PATH        记录操作日志到 JSON Lines 文件
  -h, --help             显示帮助信息

注：slm 和 lk 完全等价，可互换使用。
```

## 安全特性

1. **默认 Dry-run**：所有操作需要用户确认后才会执行。
2. **仅处理目录型符号链接**：忽略文件符号链接与损坏链接。
3. **跨卷安全移动**：自动检测跨卷错误并回退到 `copytree` + 删除。
4. **移动后验证**：确保所有符号链接 `resolve()` 到新的目标。
5. **排除噪音目录**：自动跳过 `.git`, `Library`, `.cache`, `node_modules`, `.venv`, `venv` 等常见目录。

## 目录树摘要说明

工具会显示两种摘要：

1. **Dry-run 预览摘要**：
   ```
   summary(current=files:42 bytes:1048576, new=files:12 bytes:4096)
   ```
   - `current`: 当前目标目录的文件统计
   - `new`: 新目标位置的文件统计（如不存在则为 0）

2. **执行后最终摘要**：
   ```
   summary(new=files:42 bytes:1048576)
   ```
   - 显示迁移完成后的最终状态

## 故障排查

### 问题：未找到任何符号链接

**原因**：
- 扫描范围可能不包含符号链接所在目录
- 符号链接可能指向 Data root 之外的位置

**解决方案**：
```bash
# 扩大扫描范围
slm --scan-roots ~ ~/Developer ~/Documents ~/Projects
```

### 问题：目标已存在

**当前行为**：
- 默认中止操作并提示冲突
- 可选择备份策略，将已有目标重命名为 `dest~YYYYMMDD-HHMMSS` 后继续迁移
- 强制覆盖暂不支持

### 问题：权限不足

**解决方案**：
- 确保对源目录和目标目录有读写权限
- 必要时使用 `sudo`（不推荐）

## 开发状态

当前进度：9/9 任务完成（100%）。

已完成：
- ✅ 项目初始化与依赖
- ✅ 符号链接发现器
- ✅ Questionary 多级菜单
- ✅ 迁移执行器（含跨卷回退）
- ✅ JSON 日志与树摘要
- ✅ 冲突与权限处理（备份策略）
- ✅ 配置文件支持（PyYAML）
- ✅ 测试套件（4/4 通过）
- ✅ 文档与示例更新（README、USAGE、配置说明）

## 反馈与贡献

如有问题或建议，请在项目仓库提交 Issue。
