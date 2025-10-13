# FILTERING

> 符号链接过滤功能规范（Symlink Filtering Feature）

本规范定义 `lk` 在“发现/显示符号链接”阶段的过滤语义、默认规则、配置格式与 CLI 覆盖顺序，确保在大型目录树中降低噪声、保持性能与可观测性。

## 1. 目标
- 降低噪声：隐藏无意义/外部依赖目录（如 `node_modules/`）内的符号链接。
- 保持安全：仅在“读取/匹配”层工作，不修改文件系统（符合 Invariants #5）。
- 可配置：支持 YAML 配置与 CLI 参数动态覆盖。
- 可观测：日志与报告显示规则命中与跳过统计。

## 2. 语义与优先级
- 判定单位：基于“路径字符串”（绝对/相对）与“是否为符号链接”。
- 规则字段：
  - `include`: 匹配即纳入（优先级高于 `exclude`）。
  - `exclude`: 匹配即排除（若未命中 `include`）。
  - `ignore_case`: 是否大小写不敏感（默认 false）。
  - `use_regex`: 是否将模式视为正则（默认 false，默认按 glob 处理）。
  - `max_depth`: 可选，限制扫描深度。
- 优先级：CLI > 配置文件 > 默认规则。
- 关闭过滤：`--no-filter`（忽略所有 include/exclude，仍允许 `max_depth` 生效）。

## 3. 默认规则（exclude 基础集）
以下规则默认启用，可被配置或 CLI 覆盖：

```
exclude:
  - "*/.git/*"
  - "*/.hg/*"
  - "*/.svn/*"
  - "*/node_modules/*"
  - "*/.venv/*"
  - "*/__pycache__/*"
  - "*.tmp"
  - "*.swp"
  - "*/.DS_Store"
```

## 4. 配置文件（YAML）
默认加载路径：`~/.config/lk/filter.yml`（存在则读取，无则仅用默认规则与 CLI）。

示例：

```yaml
# ~/.config/lk/filter.yml
ignore_case: false
use_regex: false
max_depth: 20
include:
  - "*/Projects/*"
exclude:
  - "*/node_modules/*"
  - "*/build/*"
  - "*/dist/*"
```

## 5. CLI 覆盖
- `--filter-config PATH` 指定配置文件路径。
- `--include PATTERN` 可多次，提升到当前会话的 include 集合。
- `--exclude PATTERN` 可多次，提升到当前会话的 exclude 集合。
- `--no-filter` 禁用 include/exclude（便于快速回滚验错）。

优先级说明：当同一路径同时被 include 与 exclude 命中，`include` 优先（用于拯救误杀）。

## 6. 性能与实现要点
- 预编译模式：glob/regex 在启动时编译一次；匹配时零分配。
- 目录级短路：若某目录命中 `exclude`，跳过整支子树扫描。
- 仅渲染可视：结合现有 TUI 视口渲染，仅对可见项目进行渲染。

## 7. 可观测性
- `data/logs/filter.log`：记录规则加载、命中统计与跳过数。
- `--debug-filter`：输出命中详情（仅调试）。
- `data/reports/filter_report.json`：针对大目录输出规则命中分布（可选）。

## 8. 验收与验证
- 通过 `lk --exclude '*/node_modules/*' --scan-path <dir>` 验证：噪声明显下降，性能不倒退。
- 配置错误能给出明确的人类可读提示，并指向问题字段。

