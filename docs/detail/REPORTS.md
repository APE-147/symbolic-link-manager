# REPORTS.md — 备份文档合并摘要（under_review）

> 目标：在不丢失信息的前提下，收敛 `backup/docs/` 中零散的研究/阶段性报告到一个可浏览入口；保留原文件作为详细依据。
>
> 更新时间：2025-10-18

---

## 一、阶段总结

- CYCLE_3_SUMMARY.md（2025-10-14）
  - 结论：已完成“三级分类体系（Primary/Secondary/Project）”；兼容旧数据模型。
  - 影响面：扫描/分类与 TUI 展示；为大规模链接整理提供层级视图。
  - 证据：新增 13 个分类相关测试，全部通过。

- PHASE2_COMPLETION_REPORT.md（2025-01-14）
  - 结论：完成 Textual TUI 的 Phase 2；替换 simple-term-menu，解决终端残留/闪烁。
  - 亮点：基于虚拟 DOM 的稳定渲染；键盘导航、详情与编辑流完整；46/46 测试通过。
  - 依赖：`textual>=0.60,<1.0`（可选依赖）。

---

## 二、研究与实现建议（TEXTUAL_*）

- TEXTUAL_RESEARCH_REPORT.md（2025-10-14）
  - 问题：终端渲染残留与闪烁源于简单菜单库缺乏虚拟 DOM/状态管理。
  - 建议：迁移至 Textual（布局系统、Rich 集成、异步事件循环）。
  - 迁移路径：主列表（三级树）→ 详情 → 编辑三屏架构；键位与状态管理对齐 Go/tview 经验。

- TEXTUAL_QUICK_REFERENCE.md / TEXTUAL_TESTING_GUIDE.md / TEXTUAL_VISUAL_COMPARISON.md
  - 内容：Textual 常用 API 速查、测试策略（快照/交互）、渲染对比与残留问题复盘。
  - 结论：Textual 在复杂 UI 下显著优于简单菜单库；建议作为可选 UI 引擎纳入。

---

## 三、与当前 slm 的差异与收敛策略

- 现状：当前 `slm` 为“Questionary 交互 + 最小安全迁移”的精简版；未集成 TUI/层级分类/过滤规则。
- 差异：备份实现包含更完整的 UI 与分类/过滤能力（`symlink_manager/**`）。
- 收敛建议：
  1) 保持 `slm` 轻量交互路线，优先补齐“冲突处理/配置文件/测试/CI”。
  2) 将 Textual TUI 作为“可选子命令或独立 extra（`slm[tui]`）”；避免强耦合。
  3) 逐步吸收“三级分类”的数据模型与展示思想，但不引入复杂依赖前先验证需求强度。

---

## 四、下一步建议（与 TASKS 对齐）

- 冲突策略（Abort/Backup）与 ISO8601 日志时间戳统一。
- 配置文件 `~/.config/slm.yml` 与优先级（CLI > 配置 > 默认）。
- 测试最小集（含跨卷迁移/符号链接验证/错误路径/权限不足等）。
- 可选：落地一个最小 Textual TUI demo（单屏只读）以验证依赖与发布策略。

---

## 附：原始文档索引（保留路径）

- backup/docs/CYCLE_3_SUMMARY.md
- backup/docs/PHASE2_COMPLETION_REPORT.md
- backup/docs/PLAN.md
- backup/docs/REQUIRES.md
- backup/docs/TASKS.md
- backup/docs/TEXTUAL_MIGRATION_SUMMARY.md
- backup/docs/TEXTUAL_QUICK_REFERENCE.md
- backup/docs/TEXTUAL_RESEARCH_REPORT.md
- backup/docs/TEXTUAL_TESTING_GUIDE.md
- backup/docs/TEXTUAL_VISUAL_COMPARISON.md

