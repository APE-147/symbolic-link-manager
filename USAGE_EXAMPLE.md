# slm 使用示例

## 快速开始

### 1. 安装

```bash
cd /Users/niceday/Developer/Cloud/Dropbox/-Code-/Scripts/system/data-storage/symbolic_link_changer
pip install -e .
```

### 2. 基本使用

#### 交互式选单（默认 dry-run）

```bash
slm
```

默认行为：
- Data root: `~/Developer/Data`
- Scan roots: `~` （用户主目录）
- Dry-run: 开启（需要确认才执行）

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
cat migration.jsonl | jq .
```

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

5. 确认 dry-run 计划：
```
计划 (dry-run):
  • Move: /Users/niceday/Developer/Data/myproject-data -> /Users/niceday/Developer/Data/archived/myproject-data
  • Link: /Users/niceday/workspace/myproject/data -> /Users/niceday/Developer/Data/archived/myproject-data
  • Link: /Users/niceday/Documents/backup/myproject-link -> /Users/niceday/Developer/Data/archived/myproject-data
summary(current=files:42 bytes:1048576, new=files:0 bytes:0)
执行上述操作吗？ (y/N):
```

6. 确认后执行，工具会：
   - 移动目录到新位置
   - 更新所有符号链接指向新位置
   - 验证符号链接正确性
   - 显示最终摘要

### 场景 2：跨卷移动（自动处理）

当目标位置在不同的文件系统/卷时，工具会自动：
- 尝试使用 `os.rename`（最快）
- 如果失败（跨卷错误），自动回退到 `shutil.copytree` + 删除原目录
- 确保数据完整性

### 场景 3：使用 JSON 日志跟踪操作

```bash
slm --log-json ./slm-operations.jsonl
```

查看操作记录：
```bash
# 查看所有操作
cat slm-operations.jsonl | jq .

# 仅查看 preview 阶段
cat slm-operations.jsonl | jq 'select(.phase == "preview")'

# 仅查看实际执行的移动操作
cat slm-operations.jsonl | jq 'select(.phase == "applied" and .type == "move")'

# 按时间排序
cat slm-operations.jsonl | jq -s 'sort_by(.ts)'
```

JSON 日志格式示例：
```json
{"phase": "preview", "type": "move", "from": "/path/old", "to": "/path/new", "ts": "2025-10-18T12:23:45"}
{"phase": "preview", "type": "retarget", "link": "/workspace/link1", "to": "/path/new", "ts": "2025-10-18T12:23:45"}
{"phase": "applied", "type": "move", "from": "/path/old", "to": "/path/new", "ts": "2025-10-18T12:24:10"}
{"phase": "applied", "type": "retarget", "link": "/workspace/link1", "to": "/path/new", "ts": "2025-10-18T12:24:10"}
```

## 命令行选项

```
slm [选项]

选项:
  --data-root PATH       Data 目录的根路径（默认: ~/Developer/Data）
  --scan-roots PATH ...  扫描符号链接的根目录列表（默认: ~）
  --dry-run              Dry-run 模式，显示计划但不执行（默认开启）
  --log-json PATH        记录操作日志到 JSON Lines 文件
  -h, --help             显示帮助信息
```

## 安全特性

1. **默认 Dry-run**：所有操作需要用户确认
2. **仅处理目录型符号链接**：忽略文件符号链接
3. **自动忽略损坏的链接**：跳过无效符号链接
4. **跨卷安全移动**：自动检测并使用安全的复制策略
5. **移动后验证**：确保所有符号链接指向正确
6. **排除噪音目录**：自动跳过 `.git`, `Library`, `node_modules`, `.venv` 等

## 目录树摘要说明

工具会显示两种摘要：

1. **Dry-run 预览摘要**：
   ```
   summary(current=files:42 bytes:1048576, new=files:0 bytes:0)
   ```
   - `current`: 当前目标目录的文件统计
   - `new`: 新目标位置的文件统计（如不存在则为 0）

2. **执行后最终摘要**：
   ```
   summary(new=files:42 bytes:1048576)
   ```
   - 显示移动后新位置的实际文件统计

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

**当前行为**：操作会失败并显示错误信息

**计划功能**（待实现）：
- 冲突处理策略（abort / backup / overwrite）
- 自动备份原目标为 `dest~TIMESTAMP`

### 问题：权限不足

**解决方案**：
- 确保对源目录和目标目录有读写权限
- 必要时使用 `sudo`（不推荐）

## 开发状态

当前进度：5/9 任务完成（56%）

已完成：
- ✅ 项目初始化与依赖
- ✅ 符号链接发现器
- ✅ Questionary 多级菜单
- ✅ 迁移执行器（含跨卷回退）
- ✅ JSON 日志与树摘要

待实现：
- ⏳ 冲突与权限处理
- ⏳ 配置文件支持
- ⏳ 测试套件
- ⏳ 完整文档

## 反馈与贡献

如有问题或建议，请在项目仓库提交 Issue。
