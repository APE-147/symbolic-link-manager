# Symlink Manager (lk)

> 安全的 macOS/Linux 符号链接扫描、分类和管理工具，具备交互式 TUI 界面。

## 快速开始

```bash
# 安装
pip install -e .[dev]

# 运行
lk --target /path/to/scan

# 使用分层分类配置
lk --target ~/Developer/Desktop --config ~/.config/lk/projects.md
```

## 核心功能

- **智能扫描**: 发现并分类符号链接（三层级：Primary → Secondary → Project）
- **交互式 TUI**: Rich 终端界面，流畅导航体验
- **智能过滤**: 减少 90%+ 噪音（模式、目录、乱码、哈希目标）
- **目标编辑**: 带验证的安全路径编辑
- **全面测试**: 44/44 测试通过 ✅

## TUI 导航键

| 键 | 功能 |
|---|---|
| ↑/↓ 或 j/k | 上下移动 |
| / | 搜索/过滤 |
| Enter | 查看详情 |
| e | 编辑目标路径 |
| q | 退出 |

## 配置示例

创建 `~/.config/lk/projects.md`:

```markdown
## Desktop
- /Users/*/Developer/Desktop/**/*

## Service
- /Users/*/Developer/Service/**/*

## System
- /Users/*/Developer/System/**/*
```

系统会自动从路径结构提取 Secondary 和 Project 层级信息。

## 技术栈

- Python 3.9+
- Rich (TUI 渲染)
- simple-term-menu (交互导航)
- pytest (测试框架)

## 测试

```bash
pytest -v         # 详细输出
pytest -q         # 快速测试
```

## 完整文档

**查看 [AGENTS.md](./AGENTS.md)** 获取完整项目文档，包括：
- 详细功能说明与使用指南
- 技术实现细节与架构设计
- 开发周期历史与决策记录
- 测试策略与手动测试清单
- 项目总结与维护指南

## 项目状态

- ✅ 所有核心功能已完成
- ✅ 44/44 测试通过
- ✅ TUI 优化完成（无闪烁、无滚动、无标题重复）
- ✅ 三层级分类系统已实现
- ⏳ 待手动终端测试验证

## 许可证

[待添加]
