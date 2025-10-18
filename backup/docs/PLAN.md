# PLAN

> 每次运行在文件底部追加一个 Cycle（6-8 个问题 + 选项效果 + 进度）。

## Cycle 1 - 2025-10-13 (@source: REQUIRES.md + analysis)
Progress: 0.00% (from TASKS.md)

### Q1. How should we handle screen clearing to prevent flickering?
- A) Use alternate screen buffer (ANSI escape sequences)
  - Effect: 范围=全局/风险=低/质量=高/复杂度=低/工期=1h/成本=低/可维护性=高/可观测性=高
  - Pros: Standard practice (vim, less, htop), clean separation from terminal scrollback
  - Cons: Requires manual ANSI sequence management
- B) Disable clear_screen in TerminalMenu and minimize console.clear() calls
  - Effect: 范围=局部/风险=低/质量=中/复杂度=极低/工期=30min/成本=极低/可维护性=中/可观测性=中
  - Pros: Simplest fix, minimal code changes
  - Cons: May not fully solve scrollback pollution
- C) Combine A + B (alternate screen + optimized clearing)
  - Effect: 范围=全局/风险=低/质量=最高/复杂度=中/工期=1.5h/成本=低/可维护性=高/可观测性=高
  - Pros: Best of both worlds, most robust solution
  - Cons: Slightly more complex

### Q2. Should we use Rich Console's screen() context manager or manual ANSI codes?
- A) Use Rich Console.screen() context manager
  - Effect: 范围=全局/风险=低/质量=高/复杂度=低/工期=30min/成本=低/可维护性=高/可观测性=高
  - Pros: Leverages existing Rich dependency, cleaner API, automatic cleanup
  - Cons: Relies on Rich's implementation
- B) Manual ANSI escape sequences (_enter_alternate_screen/_exit_alternate_screen)
  - Effect: 范围=全局/风险=中/质量=高/复杂度=中/工期=1h/成本=低/可维护性=中/可观测性=中
  - Pros: Direct control, no dependency on Rich behavior
  - Cons: More error-prone, manual cleanup required

### Q3. How to handle cursor visibility during navigation?
- A) Hide cursor during menu navigation, restore on exit
  - Effect: 范围=局部/风险=低/质量=高/复杂度=低/工期=15min/成本=极低/可维护性=高/可观测性=高
  - Pros: Reduces visual noise, cleaner appearance
  - Cons: Must ensure cursor is always restored
- B) Leave cursor management to simple-term-menu
  - Effect: 范围=无/风险=无/质量=中/复杂度=无/工期=0/成本=无/可维护性=高/可观测性=中
  - Pros: No code needed
  - Cons: May contribute to flicker

### Q4. Should we add terminal size detection and adaptive behavior?
- A) Detect terminal size, disable preview on small terminals (<100 cols)
  - Effect: 范围=局部/风险=低/质量=高/复杂度=低/工期=30min/成本=低/可维护性=高/可观测性=高
  - Pros: Better UX on small terminals, prevents overflow issues
  - Cons: Additional complexity
- B) Keep current behavior (fixed preview_size=0.3)
  - Effect: 范围=无/风险=无/质量=中/复杂度=无/工期=0/成本=无/可维护性=高/可观测性=中
  - Pros: Simpler
  - Cons: May be cramped on small terminals

### Q5. How to handle transitions between menu/detail/edit views?
- A) Clear screen cleanly before each view switch
  - Effect: 范围=局部/风险=低/质量=高/复杂度=低/工期=30min/成本=低/可维护性=高/可观测性=高
  - Pros: Clean visual transitions
  - Cons: Requires consistent clearing pattern
- B) Use console.clear() only once at start, rely on overwrites
  - Effect: 范围=局部/风险=中/质量=中/复杂度=低/工期=15min/成本=低/可维护性=中/可观测性=中
  - Pros: Minimal clearing
  - Cons: May leave artifacts

### Q6. Should we limit menu height to prevent scrolling?
- A) Add menu_entries_max_height parameter to TerminalMenu
  - Effect: 范围=局部/风险=低/质量=高/复杂度=低/工期=15min/成本=极低/可维护性=高/可观测性=高
  - Pros: Prevents menu from exceeding screen height
  - Cons: May require scrolling for long lists
- B) Let simple-term-menu handle it automatically
  - Effect: 范围=无/风险=无/质量=中/复杂度=无/工期=0/成本=无/可维护性=高/可观测性=中
  - Pros: Simpler
  - Cons: Library may not handle all edge cases

### Q7. How to ensure clean exit and terminal restoration?
- A) Use try/finally block to guarantee cleanup
  - Effect: 范围=全局/风险=低/质量=高/复杂度=低/工期=15min/成本=极低/可维护性=高/可观测性=高
  - Pros: Ensures terminal always restored, even on errors
  - Cons: Slightly more verbose
- B) Rely on context manager cleanup (if using Console.screen())
  - Effect: 范围=全局/风险=低/质量=高/复杂度=极低/工期=0/成本=无/可维护性=高/可观测性=高
  - Pros: Pythonic, automatic cleanup
  - Cons: Requires using context manager

### Q8. Should we add manual testing checklist to docs?
- A) Create docs/TESTING.md with manual test scenarios
  - Effect: 范围=文档/风险=无/质量=高/复杂度=低/工期=20min/成本=低/可维护性=高/可观测性=高
  - Pros: Ensures thorough testing, reproducible validation
  - Cons: Extra documentation to maintain
- B) Document testing in commit message only
  - Effect: 范围=git历史/风险=低/质量=中/复杂度=无/工期=0/成本=无/可维护性=中/可观测性=低
  - Pros: Simpler
  - Cons: Less discoverable

### 建议与权衡:
- 建议: Q1→C, Q2→A, Q3→A, Q4→A, Q5→A, Q6→A, Q7→B, Q8→A
- 理由:
  1. 组合方案（alternate screen + 优化clearing）提供最佳体验
  2. Rich Console.screen() 更简洁且自动清理
  3. 隐藏光标减少视觉噪音
  4. 终端尺寸检测提升小屏体验
  5. 清晰的视图切换提升UX
  6. 限制菜单高度防止滚动
  7. Context manager 确保清理
  8. 测试清单确保质量

## Cycle 2 - 2025-10-14 (@source: REQUIRES.md + PLAN prompt)
Progress: 100.00% (from TASKS.md)

### Q1. 如何处理菜单标题以消除重复行？
- A) 移除 TerminalMenu 的 `title`，用 Rich 在菜单上方自绘单行标题
  - Effect: 范围=局部/风险=低/质量=高/复杂度=低/工期=30min/成本=低/可维护性=高/可观测性=高
  - Pros: 避免库重复绘制；可控样式；与 alternate buffer 兼容
  - Cons: 需手动管理回到菜单时的标题重绘
- B) 保留 `title` 但将 `clear_screen=True`
  - Effect: 范围=局部/风险=中/质量=中/复杂度=低/工期=15min/成本=低/可维护性=中/可观测性=中
  - Pros: 由库负责清屏与重绘
  - Cons: 可能重新引入抖动/闪屏问题（已在 Cycle 1 避免）
- C) 继续使用 `title`，进入/退出时注入 ANSI 控制序列（光标复位+区域擦除）
  - Effect: 范围=局部/风险=中/质量=中/复杂度=中/工期=45min/成本=低/可维护性=中/可观测性=中
  - Pros: 精细控制重绘区域
  - Cons: 易错、与库输出交互复杂

### Q2. 标题的重绘时机？
- A) 每次回到主菜单前清屏并重绘标题，再 `menu.show()`
  - Effect: 范围=局部/风险=低/质量=高/复杂度=低/工期=20min/成本=低/可维护性=高/可观测性=高
  - Pros: 干净、可预期；不依赖库的起始行位置
  - Cons: 视图切换瞬间可能有轻微闪烁
- B) 仅首次进入时绘制标题，后续完全交给菜单重绘
  - Effect: 范围=局部/风险=中/质量=中/复杂度=低/工期=10min/成本=低/可维护性=中/可观测性=中
  - Pros: 最少清屏
  - Cons: 细节页返回后菜单可能在标题下方错位
- C) 维护一个 `needs_header_refresh` 标志，仅在从详情/编辑返回时重绘
  - Effect: 范围=局部/风险=低/质量=高/复杂度=中/工期=30min/成本=低/可维护性=高/可观测性=高
  - Pros: 减少不必要清屏，避免重复
  - Cons: 需谨慎管理状态

### Q3. 标题呈现样式？
- A) 简单单行文本（轻样式）
  - Effect: 范围=UI/风险=低/质量=高/复杂度=低/工期=10min/成本=低/可维护性=高/可观测性=高
  - Pros: 最稳定、最不易造成布局抖动
  - Cons: 视觉吸引力一般
- B) Rich Panel（有边框/标题）
  - Effect: 范围=UI/风险=低/质量=中/复杂度=低/工期=15min/成本=低/可维护性=高/可观测性=高
  - Pros: 更醒目
  - Cons: 占用行高，可能压缩可见菜单项
- C) 顶部状态栏（Rich Text + rule）
  - Effect: 范围=UI/风险=低/质量=高/复杂度=中/工期=20min/成本=低/可维护性=高/可观测性=高
  - Pros: 信息密度高
  - Cons: 代码稍复杂

### Q4. 菜单与详情/编辑的切换策略？
- A) 从详情/编辑返回主菜单时执行 `console.clear()` + 标题重绘
  - Effect: 范围=局部/风险=低/质量=高/复杂度=低/工期=15min/成本=低/可维护性=高/可观测性=高
  - Pros: 最干净的回切体验
  - Cons: 轻微清屏成本
- B) 依赖库在原区域重绘（不清屏）
  - Effect: 范围=局部/风险=中/质量=中/复杂度=低/工期=10min/成本=低/可维护性=中/可观测性=中
  - Pros: 少一次清屏
  - Cons: 容易出现叠画/错行

### Q5. 预览窗与标题并存的布局策略？
- A) 保持现有 `preview_size` 自适应（≥100列：0.3；否则：0）
  - Effect: 范围=布局/风险=低/质量=高/复杂度=低/工期=0/成本=无/可维护性=高/可观测性=高
  - Pros: 与现有逻辑一致，风险低
  - Cons: 无
- B) 宽屏时略微下调 `preview_size`（如 0.25）
  - Effect: 范围=布局/风险=低/质量=中/复杂度=低/工期=10min/成本=低/可维护性=高/可观测性=中
  - Pros: 腾出更多行给菜单
  - Cons: 预览信息略少

### Q6. 键盘提示放置位置？
- A) 继续使用 TerminalMenu `status_bar`
  - Effect: 范围=UI/风险=低/质量=高/复杂度=低/工期=0/成本=无/可维护性=高/可观测性=高
  - Pros: 库内置，简单稳定
  - Cons: 样式可定制性有限
- B) 自绘底部提示栏（Rich）
  - Effect: 范围=UI/风险=低/质量=中/复杂度=中/工期=20min/成本=低/可维护性=高/可观测性=高
  - Pros: 可与标题风格统一
  - Cons: 需管理与菜单的相对位置

### Q7. 兼容性验证范围？
- A) 先验证 macOS Terminal.app（必测），再扩展 iTerm2/Alacritty（可选）
  - Effect: 范围=测试/风险=低/质量=高/复杂度=低/工期=20min/成本=低/可维护性=高/可观测性=高
  - Pros: 先满足主要环境，逐步扩大
  - Cons: 初期覆盖面较窄
- B) 一次性覆盖 3 个终端
  - Effect: 范围=测试/风险=低/质量=高/复杂度=中/工期=45min/成本=低/可维护性=高/可观测性=高
  - Pros: 一次性心安
  - Cons: 时间稍长

### 建议与权衡（Cycle 2）
- 建议: Q1→A, Q2→A, Q3→A, Q4→A, Q5→A, Q6→A, Q7→A
- 理由:
  1. 取消库内标题最直接消除重复问题
  2. 回到菜单前清屏+重绘标题最稳定
  3. 单行标题占用最少行高，风险最低
  4. 维持现有预览自适应逻辑，减少变化面
  5. 延续库内置 `status_bar` 实现
  6. 先满足主要终端，再逐步扩展

## Cycle 3 - 2025-10-14 (@source: REQUIRES.md + PLAN prompt.md)
Progress: 0.00% (from TASKS.md - new feature)

### Q1. 配置文件解析方案：如何实现3层级配置结构？
- A) 扩展现有parser，增加 `###` 标题支持，构建嵌套OrderedDict ★
  - Effect: 范围=classifier.py/风险=低/质量=高/复杂度=中/工期=1-2h/成本=低/可维护性=高/可观测性=高
  - Pros: 保留现有parse逻辑；渐进式扩展；易于测试
  - Cons: 需重构数据结构
- B) 全新parser实现，使用dataclass建模3层级（Primary/Secondary/Project）
  - Effect: 范围=classifier.py/风险=中/质量=最高/复杂度=高/工期=2-3h/成本=中/可维护性=最高/可观测性=最高
  - Pros: 类型安全；清晰语义；IDE友好
  - Cons: 工期稍长；需重写parse_markdown_config_text
- C) 保持现有flat结构，用 `Primary/Secondary` 作key
  - Effect: 范围=classifier.py局部/风险=极低/质量=中/复杂度=低/工期=30min/成本=极低/可维护性=中/可观测性=中
  - Pros: 最小改动；无需数据模型重构
  - Cons: 不符合用户层次化预期；TUI展示受限
使用方案A

### Q2. 数据模型设计：SymlinkInfo如何表示3层分类？
- A) 新增3个字段：primary_category / secondary_category / project_name ★
  - Effect: 范围=scanner.py dataclass/风险=低/质量=高/复杂度=低/工期=30min/成本=低/可维护性=高/可观测性=高
  - Pros: 语义明确；向后兼容（保留project字段）；TUI易于遍历
  - Cons: dataclass字段变多
- B) 单字段 `hierarchy: Tuple[str, str, str]`
  - Effect: 范围=scanner.py dataclass/风险=低/质量=中/复杂度=低/工期=20min/成本=低/可维护性=中/可观测性=中
  - Pros: 紧凑；类型统一
  - Cons: 字段语义不直观；需索引访问
- C) 保留现有 `project` 字段，用 `/` 分隔层级（如 `Desktop/Projects/ProjectAlpha`）
  - Effect: 范围=无需dataclass改动/风险=极低/质量=低/复杂度=低/工期=15min/成本=极低/可维护性=低/可观测性=低
  - Pros: 零dataclass改动
  - Cons: 字符串解析易错；TUI需split逻辑
使用方案A

### Q3. 向后兼容策略：如何处理现有flat配置？
- A) Parser自动检测：无 `###` 则fallback到flat模式，填充 `primary="unclassified"` ★
  - Effect: 范围=classifier.py parser/风险=低/质量=高/复杂度=中/工期=1h/成本=低/可维护性=高/可观测性=高
  - Pros: 用户无感知；平滑升级；现有配置继续工作
  - Cons: parser逻辑需if分支
- B) 强制迁移：要求用户将flat配置改为 `## Unclassified / ### Default` 格式
  - Effect: 范围=全局/风险=高/质量=中/复杂度=低/工期=30min/成本=高（用户迁移）/可维护性=中/可观测性=中
  - Pros: parser简单；无兼容负担
  - Cons: 破坏性变更；用户体验差
- C) 双parser：flat_parser + hierarchical_parser，运行时选择
  - Effect: 范围=classifier.py/风险=低/质量=高/复杂度=高/工期=2h/成本=中/可维护性=中/可观测性=高
  - Pros: 清晰分离；易于测试
  - Cons: 代码重复；维护两套逻辑
使用方案A

### Q4. TUI展示方式：3层级如何可视化？
- A) 缩进显示：`[PRIMARY]` → `  [Secondary]` → `    ✓ project` ★
  - Effect: 范围=tui.py menu building/风险=低/质量=高/复杂度=中/工期=1-1.5h/成本=低/可维护性=高/可观测性=高
  - Pros: 直观层级；与原需求示例一致；ASCII友好
  - Cons: 宽屏占用稍多
- B) 树形字符：`└─ / ├─` 风格
  - Effect: 范围=tui.py menu building/风险=低/质量=中/复杂度=高/工期=2h/成本=中/可维护性=中/可观测性=高
  - Pros: 视觉美观
  - Cons: 字符集兼容性问题；复杂度高
- C) 平铺 + 颜色标记：`[Desktop:Projects] ProjectAlpha`
  - Effect: 范围=tui.py/风险=低/质量=中/复杂度=低/工期=45min/成本=低/可维护性=高/可观测性=中
  - Pros: 简单实现
  - Cons: 层级不直观
使用方案B

### Q5. 分类逻辑实现：classify_symlinks如何处理3层匹配？
- A) 三重嵌套循环：primary → secondary → pattern，first-match原则 ★
  - Effect: 范围=classifier.py classify函数/风险=低/质量=高/复杂度=中/工期=1h/成本=低/可维护性=高/可观测性=高
  - Pros: 逻辑清晰；与现有算法一致（顺序匹配）
  - Cons: 性能O(n*m*k)，但实际影响小
- B) 预构建pattern→(primary,secondary)映射表
  - Effect: 范围=classifier.py/风险=低/质量=高/复杂度=高/工期=1.5h/成本=中/可维护性=中/可观测性=高
  - Pros: 性能优化（O(n*p)）
  - Cons: 需额外数据结构；顺序语义丢失
- C) 保持flat classify，后处理split project字段
  - Effect: 范围=classifier.py + tui.py/风险=中/质量=低/复杂度=中/工期=1h/成本=低/可维护性=低/可观测性=低
  - Pros: 分类逻辑不变
  - Cons: 耦合split逻辑；不符合设计
使用方案A

### Q6. 测试策略：如何覆盖3层分类逻辑？
- A) 新增tests/test_hierarchical_classifier.py，覆盖parser + classify + TUI menu building ★
  - Effect: 范围=tests/风险=无/质量=最高/复杂度=中/工期=1-1.5h/成本=低/可维护性=高/可观测性=最高
  - Pros: 独立测试文件；清晰组织；易于CI
  - Cons: 需编写mock config与symlinks
- B) 扩展现有test_classifier.py
  - Effect: 范围=tests/风险=低/质量=高/复杂度=低/工期=45min/成本=低/可维护性=中/可观测性=高
  - Pros: 保持测试集中
  - Cons: 单文件变大；flat/hierarchical混合
- C) 仅手工测试 + 示例配置验证
  - Effect: 范围=手工/风险=高/质量=低/复杂度=无/工期=30min/成本=极低/可维护性=低/可观测性=极低
  - Pros: 快速验证
  - Cons: 无回归保护；不符合CI要求
使用方案A

### Q7. 示例配置文件：放置位置与内容？
- A) ~/.config/lk/projects.md，包含Desktop/Service/System 3个primary示例 ★
  - Effect: 范围=文档+示例/风险=无/质量=高/复杂度=低/工期=30min/成本=低/可维护性=高/可观测性=高
  - Pros: 用户标准路径；与需求示例对齐；易于发现
  - Cons: 需README说明
- B) docs/example_hierarchical_config.md
  - Effect: 范围=文档/风险=无/质量=中/复杂度=低/工期=20min/成本=低/可维护性=高/可观测性=中
  - Pros: 不污染用户目录
  - Cons: 用户需手动复制
- C) 仅README中嵌入代码块
  - Effect: 范围=文档/风险=无/质量=低/复杂度=极低/工期=10min/成本=极低/可维护性=中/可观测性=低
  - Pros: 最简单
  - Cons: 用户体验差
使用方案A

### Q8. 工期与风险评估：整体实施计划？
- A) 分3个micro-PR：1)data model+parser, 2)classifier logic, 3)TUI display ★
  - Effect: 范围=全局/风险=最低/质量=最高/复杂度=中/工期=5-6h total/成本=中/可维护性=最高/可观测性=最高
  - Pros: 渐进验证；每步可回滚；清晰commit历史
  - Cons: 需规划子任务顺序
- B) 单次完整实现（1个PR）
  - Effect: 范围=全局/风险=中/质量=高/复杂度=高/工期=4-5h/成本=中/可维护性=高/可观测性=高
  - Pros: 原子性；测试一次性通过
  - Cons: 出错回滚大；review负担重
- C) 先MVP（仅parser+基础TUI），后续迭代完善
  - Effect: 范围=渐进/风险=低/质量=中/复杂度=低/工期=2-3h MVP/成本=低/可维护性=中/可观测性=中
  - Pros: 快速交付可用版本
  - Cons: 需二次迭代；用户预期管理
使用方案B

### 建议与权衡（Cycle 3）
- 建议: Q1→B（高质量dataclass），Q2→A（3字段），Q3→A（auto-detect），Q4→A（缩进），Q5→A（三重循环），Q6→A（独立测试文件），Q7→A（~/.config示例），Q8→B（单PR原子实现）
- 理由:
  1. dataclass建模提供类型安全与最佳可维护性，工期可控（2-3h）
  2. 3字段设计语义清晰，TUI遍历友好
  3. 自动检测flat兼容，用户体验平滑
  4. 缩进显示符合需求示例，实现简单
  5. 三重循环逻辑直观，性能足够
  6. 独立测试文件保障质量，易于CI
  7. ~/.config示例符合用户习惯
  8. 单PR原子实现保证测试完整性（权衡：若工期紧张可改Q8→A分步）

### 加权评分（Pugh，权重 UX 0.35 | 代码整洁 0.30 | 部署便捷 0.20 | 安全 0.10 | 成本 0.05）
- Q1: A=3.9, B=4.5 ★, C=3.2
- Q2: A=4.3 ★, B=3.7, C=3.1
- Q3: A=4.6 ★, B=2.8, C=3.9
- Q4: A=4.5 ★, B=3.8, C=3.3
- Q5: A=4.4 ★, B=4.1, C=3.2
- Q6: A=4.7 ★, B=4.0, C=2.5
- Q7: A=4.4 ★, B=3.8, C=3.0
- Q8: A=4.2, B=4.3 ★, C=3.6

## Cycle 4 - 2025-10-14 (@source: REQUIRES.md + internal analysis)
Progress: 100.00% (from TASKS.md - Cycle 3 complete)

> **Context**: Cycle 3 complete (44/44 tests pass). 3-level hierarchical classification working. Now exploring next optimization/enhancement directions based on user needs and technical debt analysis.

### Q1. 配置格式增强：是否支持更灵活的层级定义？
- A) 保持当前简化格式（一级手动，二三级自动检测） ★
  - Effect: 范围=无/风险=无/质量=高/复杂度=无/工期=0/成本=无/可维护性=高/可观测性=高
  - Pros: 简单；自动检测逻辑已验证；用户体验良好
  - Cons: 对复杂项目结构可能缺乏细粒度控制
- B) 允许手动指定所有三级（## / ### / - 完整层级）
  - Effect: 范围=classifier.py/风险=低/质量=高/复杂度=中/工期=2-3h/成本=低/可维护性=中/可观测性=高
  - Pros: 最大灵活性；适合复杂组织结构
  - Cons: 配置复杂度提升；需向后兼容
- C) 混合模式：支持显式 ### + 自动检测回退
  - Effect: 范围=classifier.py/风险=中/质量=高/复杂度=高/工期=3-4h/成本=中/可维护性=中/可观测性=高
  - Pros: 最大灵活性+便利性
  - Cons: 解析逻辑复杂；维护成本高
使用方案A


### Q2. TUI 显示优化：如何改进三层级可视化？
- A) 保持当前缩进风格（每级 2 空格） ★
  - Effect: 范围=无/风险=无/质量=高/复杂度=无/工期=0/成本=无/可维护性=高/可观测性=高
  - Pros: 清晰；ASCII 兼容；已验证
  - Cons: 层级多时可能缩进过深
- B) 使用 Box Drawing 字符（└─/├─）美化显示
  - Effect: 范围=tui.py/风险=低/质量=中/复杂度=低/工期=1h/成本=低/可维护性=高/可观测性=高
  - Pros: 视觉美观；现代感
  - Cons: 字符集兼容性需验证（某些终端）
- C) 可折叠层级显示（按 Space 展开/折叠分类）
  - Effect: 范围=tui.py/风险=中/质量=高/复杂度=高/工期=4-5h/成本=中/可维护性=中/可观测性=高
  - Pros: 大型项目导航友好；减少视觉噪音
  - Cons: 状态管理复杂；simple-term-menu 限制
使用方案B

### Q3. 符号链接批量操作：是否实现多选与批量编辑？
- A) 保持当前单选单编辑 ★
  - Effect: 范围=无/风险=无/质量=高/复杂度=无/工期=0/成本=无/可维护性=高/可观测性=高
  - Pros: 简单；安全；MVP 足够
  - Cons: 批量操作效率低
- B) 添加多选支持（Space 选中，Enter 确认批量操作）
  - Effect: 范围=tui.py + services/风险=中/质量=高/复杂度=高/工期=5-6h/成本=中/可维护性=中/可观测性=高
  - Pros: 提升效率；适合批量迁移场景
  - Cons: 错误风险增大；需要撤销机制
- C) 仅支持批量验证（选中多个查看验证结果，不实际修改）
  - Effect: 范围=tui.py/风险=低/质量=中/复杂度=中/工期=2h/成本=低/可维护性=高/可观测性=高
  - Pros: 安全；有助于规划批量操作
  - Cons: 仍需逐个编辑
使用方案A

### Q4. 配置文件热重载：是否支持运行时重新加载配置？
- A) 保持当前启动时加载一次 ★
  - Effect: 范围=无/风险=无/质量=高/复杂度=无/工期=0/成本=无/可维护性=高/可观测性=高
  - Pros: 简单；可预测
  - Cons: 配置修改需重启
- B) 添加 'r' 热键重新加载配置与重新分类
  - Effect: 范围=tui.py + classifier/风险=低/质量=高/复杂度=中/工期=1.5h/成本=低/可维护性=高/可观测性=高
  - Pros: 配置调试友好；无需重启
  - Cons: 状态重置可能导致导航丢失
- C) 文件监控自动重载（watchdog）
  - Effect: 范围=tui.py + 新依赖/风险=中/质量=中/复杂度=高/工期=3h/成本=中/可维护性=中/可观测性=中
  - Pros: 完全自动化
  - Cons: 新依赖；后台线程复杂度
使用方案A

### Q5. 导出功能：是否提供分类结果导出？
- A) 无导出功能（纯交互式工具） ★
  - Effect: 范围=无/风险=无/质量=高/复杂度=无/工期=0/成本=无/可维护性=高/可观测性=高
  - Pros: 保持简单
  - Cons: 无法与其他工具集成
- B) 添加 JSON 导出（按 'x' 导出当前分类结果到文件）
  - Effect: 范围=tui.py + cli/风险=低/质量=高/复杂度=低/工期=1h/成本=低/可维护性=高/可观测性=高
  - Pros: 便于自动化流程；数据可复用
  - Cons: 需定义导出格式
- C) 多格式导出（JSON/CSV/Markdown）
  - Effect: 范围=tui.py + cli + 新模块/风险=低/质量=高/复杂度=中/工期=2-3h/成本=中/可维护性=高/可观测性=高
  - Pros: 灵活性最大；适配多种用例
  - Cons: 维护多个格式
使用方案A

### Q6. 性能优化：如何处理超大规模符号链接场景（1000+）？
- A) 保持当前实现（适合 <500 符号链接） ★
  - Effect: 范围=无/风险=无/质量=高/复杂度=无/工期=0/成本=无/可维护性=高/可观测性=高
  - Pros: 实现简单；满足当前用例
  - Cons: 大规模场景可能慢
- B) 添加分页加载（TUI 每页 100 项，按需加载）
  - Effect: 范围=tui.py + scanner/风险=中/质量=高/复杂度=高/工期=4h/成本=中/可维护性=中/可观测性=高
  - Pros: 支持无限规模；内存友好
  - Cons: 导航体验可能受影响
- C) 并行扫描（多进程/多线程）+ 增量更新
  - Effect: 范围=scanner.py/风险=高/质量=中/复杂度=高/工期=5-6h/成本=高/可维护性=低/可观测性=中
  - Pros: 最快扫描速度
  - Cons: 复杂度高；容易引入并发 bug
使用方案A

### Q7. 错误处理与可恢复性：是否增强编辑失败后的恢复机制？
- A) 保持当前验证+提示（不实际修改） ★
  - Effect: 范围=无/风险=无/质量=高/复杂度=无/工期=0/成本=无/可维护性=高/可观测性=高
  - Pros: 最安全；无风险
  - Cons: 仅验证，无实际修改功能
- B) 实现原子性修改（备份→修改→验证→提交/回滚）
  - Effect: 范围=services/风险=中/质量=高/复杂度=中/工期=3-4h/成本=中/可维护性=高/可观测性=高
  - Pros: 支持实际修改；安全可回滚
  - Cons: 需要备份机制与存储空间
- C) 操作日志与撤销栈（支持 Undo/Redo）
  - Effect: 范围=services/ + tui/风险=高/质量=高/复杂度=高/工期=6-8h/成本=高/可维护性=中/可观测性=高
  - Pros: 最强容错能力；用户友好
  - Cons: 实现复杂；状态管理困难
使用方案A

### Q8. 文档与示例：如何改进用户上手体验？
- A) 保持当前文档（README + AGENTS.md） ★
  - Effect: 范围=无/风险=无/质量=高/复杂度=无/工期=0/成本=无/可维护性=高/可观测性=高
  - Pros: 已足够详细
  - Cons: 缺少交互式教程
- B) 添加 --demo 模式（使用示例数据演示功能）
  - Effect: 范围=cli.py + 新 demo 数据/风险=低/质量=高/复杂度=低/工期=1h/成本=低/可维护性=高/可观测性=高
  - Pros: 新用户友好；快速上手
  - Cons: 需要维护示例数据
- C) 交互式配置向导（首次运行引导配置文件生成）
  - Effect: 范围=cli.py/风险=低/质量=高/复杂度=中/工期=2-3h/成本=低/可维护性=高/可观测性=高
  - Pros: 零配置门槛；最友好
  - Cons: 增加启动流程复杂度

### 建议与权衡（Cycle 4）
- 建议: Q1→A（保持简化格式），Q2→A（保持缩进），Q3→A（保持单选），Q4→B（热重载），Q5→B（JSON 导出），Q6→A（保持当前），Q7→A（保持验证），Q8→B（添加 demo 模式）
- 理由:
  1. **稳定性优先**：Cycle 3 完成后优先巩固现有功能，不盲目追求复杂性
  2. **用户体验微增量**：添加热重载（Q4→B）和 demo 模式（Q8→B）投入小收益高
  3. **数据可复用性**：JSON 导出（Q5→B）支持自动化流程集成，工期短（1h）
  4. **避免过度工程**：批量操作、折叠显示、并行扫描虽好，但当前场景非刚需
  5. **渐进式演化**：先满足 80% 用例，待用户反馈后再决定是否实施 Q2-B/Q3-B/Q6-B

### 替代方案（若用户反馈需要增强）
- **若频繁修改配置** → 实施 Q4→B（热重载，1.5h）
- **若视觉体验重要** → 实施 Q2→B（Box Drawing，1h）
- **若批量迁移场景** → 实施 Q3→C 先（批量验证，2h），再考虑 Q3→B
- **若超大规模** → 实施 Q6→B（分页，4h）

### 加权评分（Pugh，权重 UX 0.35 | 稳定性 0.30 | 投入产出比 0.20 | 可维护性 0.10 | 风险 0.05）
- Q1: A=4.8 ★, B=3.9, C=3.4
- Q2: A=4.7 ★, B=4.0, C=3.2
- Q3: A=4.6 ★, B=3.5, C=3.8
- Q4: A=3.9, B=4.5 ★, C=3.6
- Q5: A=3.8, B=4.6 ★, C=4.0
- Q6: A=4.5 ★, B=3.8, C=3.0
- Q7: A=4.7 ★, B=4.1, C=3.3
- Q8: A=4.0, B=4.5 ★, C=4.2

## Cycle 5 - 2025-10-14 (@source: REQUIRES.md + internal template)
Progress: 0.00% (from TASKS.md)

### Q1. 组件架构：如何组织 Textual 的 App/Screen/Widget？
- A) 单屏单体：`App` + 顶部 `Header`/底部 `Footer` + 中间 `DataTable`/`Tree`（控制器内持久状态）
  - Effect: 范围=UI结构/风险=低/质量=中/复杂度=低/工期=0.5d/成本=低/可维护性=中/可观测性=中
  - Pros: 学习曲线低，起步快
  - Cons: 模块边界不清晰，后期扩展成本高
- B) 多 `Screen` 分层：主列表/详情/编辑分屏；每屏由若干 Widget 组成（列表、信息面板、命令栏） ★
  - Effect: 范围=UI结构/风险=低/质量=高/复杂度=中/工期=1d/成本=低/可维护性=高/可观测性=高
  - Pros: 职责清晰，路由化导航便于维护与测试
  - Cons: 首次搭建投入略高
- C) 单屏 + `ContentSwitcher` 区域切换
  - Effect: 范围=UI结构/风险=低/质量=中/复杂度=中/工期=0.75d/成本=低/可维护性=中/可观测性=中
  - Pros: 代码集中，状态管理相对简单
  - Cons: 容易变成“巨屏”，可读性下降

### Q2. 迁移策略：如何从 simple-term-menu 过渡到 Textual？
- A) 并行实现（推荐）：保留 `tui.py`，新增 `tui_textual.py`，CLI 增加 `--ui-engine=simple|textual`，默认 simple ★
  - Effect: 范围=CLI+UI/风险=低/质量=高/复杂度=中/工期=1d/成本=低/可维护性=高/可观测性=高
  - Pros: 零停机硬切换风险，支持 A/B 对比与逐步放量
  - Cons: 双实现期间维护成本略增
- B) 一次性切换（big-bang）
  - Effect: 范围=全局/风险=高/质量=不可控/复杂度=中/工期=0.5d/成本=低/可维护性=中/可观测性=中
  - Pros: 最少分支
  - Cons: 回滚困难，问题暴露集中
- C) 影子模式：新增隐藏开关（环境变量/实验标志）
  - Effect: 范围=CLI/风险=低/质量=高/复杂度=低/工期=0.5d/成本=低/可维护性=高/可观测性=高
  - Pros: 开启小流量灰度测试
  - Cons: 可发现性较低

### Q3. 事件与并发：如何与 Textual 的 asyncio 模型集成？
- A) 全面 async 化：核心服务改为 async/await，I/O 非阻塞
  - Effect: 范围=核心+UI/风险=中/质量=高/复杂度=高/工期=2-3d/成本=中/可维护性=高/可观测性=高
  - Pros: 理想架构，长期收益
  - Cons: 改动面大，回归成本高
- B) 同步核心不改，耗时操作用 `run_in_thread()/to_thread()` 下沉（推荐） ★
  - Effect: 范围=UI集成/风险=低/质量=高/复杂度=中/工期=1d/成本=低/可维护性=高/可观测性=高
  - Pros: 兼容现有同步扫描/分类代码，快速接入，不阻塞 UI
  - Cons: 线程池/任务生命周期需管理
- C) 独立进程工作者（multiprocessing）
  - Effect: 范围=服务层/风险=中/质量=高/复杂度=中/工期=1.5d/成本=中/可维护性=中/可观测性=高
  - Pros: 隔离更彻底
  - Cons: 进程间通信与部署复杂度提升

### Q4. 功能对齐：如何实现现有 3 层级浏览、搜索与编辑？
- A) 使用 `Tree`/`DataTable` 表现层级；右侧 `Info` 面板；`Modal` 进行编辑；键位对齐（↑/↓/j/k、/ 搜索、Enter 详情、e 编辑、q 退出） ★
  - Effect: 范围=UI功能/风险=低/质量=高/复杂度=中/工期=1.5d/成本=低/可维护性=高/可观测性=高
  - Pros: 完整对标现有 TUI；用户学习成本为零
  - Cons: 初期实现工作量略高
- B) 最小可用：仅列表+详情，编辑后续补齐
  - Effect: 范围=UI功能/风险=中/质量=中/复杂度=低/工期=0.5d/成本=低/可维护性=高/可观测性=中
  - Pros: 交付快
  - Cons: 影响验收标准（功能不齐）
- C) 引入高级组件（虚拟滚动、列排序等）优先
  - Effect: 范围=UI功能/风险=中/质量=中/复杂度=中/工期=1d/成本=低/可维护性=中/可观测性=中
  - Pros: 体验更强
  - Cons: 偏离“对齐现有功能”的优先级

### Q5. 测试策略：如何保证 44/44 + 新 UI 的稳定性？
- A) 保留现有单元测试；新增 Textual Pilot 驱动的 UI 行为测试（键位、焦点、筛选）；关键组件（分类/过滤）继续纯单元测试 ★
  - Effect: 范围=测试/风险=低/质量=高/复杂度=中/工期=1d/成本=低/可维护性=高/可观测性=高
  - Pros: 回归面覆盖全面，定位高效
  - Cons: 少量 UI 测试需要稳定选择器与约定
- B) 仅保留集成测试，人工回归 UI
  - Effect: 范围=测试/风险=中/质量=中/复杂度=低/工期=0.5d/成本=低/可维护性=中/可观测性=中
  - Pros: 用例编写量少
  - Cons: 容易漏边界，稳定性欠佳
- C) 截图（金图）
  - Effect: 范围=测试/风险=中/质量=中/复杂度=中/工期=1d/成本=低/可维护性=中/可观测性=中
  - Pros: 直接对比 UI 呈现
  - Cons: 对终端/字体依赖强，脆弱

### Q6. 性能与可扩展性：大数据量（>5k symlinks）如何保证流畅？
- A) 预计算+增量更新：分类/过滤在工作线程中计算，UI 仅消费 diff；使用 Textual `DataTable`/`Tree` 的虚拟化能力（推荐） ★
  - Effect: 范围=性能/风险=低/质量=高/复杂度=中/工期=1d/成本=低/可维护性=高/可观测性=高
  - Pros: UI 不阻塞，滚动流畅
  - Cons: 需要设计 diff 协议
- B) 直接重建视图（每次过滤全量重渲）
  - Effect: 范围=性能/风险=中/质量=中/复杂度=低/工期=0.5d/成本=低/可维护性=中/可观测性=中
  - Pros: 实现简单
  - Cons: 大数据下卡顿明显
- C) 引入缓存层（LRU/索引）
  - Effect: 范围=性能/风险=低/质量=高/复杂度=中/工期=1d/成本=低/可维护性=中/可观测性=中
  - Pros: 重用结果，减少计算
  - Cons: 需一致性管理

### Q7. 回滚与切换：失败时如何安全回退？
- A) CLI 开关 + 环境变量双重保险（`--ui-engine` 优先；`LK_UI_ENGINE` 兜底），默认 `simple` ★
  - Effect: 范围=发布/风险=低/质量=高/复杂度=低/工期=0.5d/成本=低/可维护性=高/可观测性=高
  - Pros: 快速切换/回滚，便于问题隔离
  - Cons: 配置路径需要文档说明
- B) 独立入口命令（如 `lk-textual`）
  - Effect: 范围=发布/风险=低/质量=中/复杂度=低/工期=0.5d/成本=低/可维护性=中/可观测性=中
  - Pros: 清晰分离
  - Cons: 可发现性与一致性稍差
- C) 一刀切删除 simple-term-menu
  - Effect: 范围=发布/风险=高/质量=中/复杂度=低/工期=0.25d/成本=低/可维护性=中/可观测性=中
  - Pros: 依赖更少
  - Cons: 不可回退

### Q8. 依赖与打包：如何引入 Textual？
- A) 可选依赖：`.[textual]` extra，默认不安装；启用 Textual 时提示安装 ★
  - Effect: 范围=打包/风险=低/质量=高/复杂度=低/工期=0.25d/成本=低/可维护性=高/可观测性=高
  - Pros: 减少默认体积，易于控制
  - Cons: 首次使用需一次安装
- B) 强制依赖：直接加入 `install_requires`
  - Effect: 范围=打包/风险=低/质量=高/复杂度=低/工期=0.1d/成本=低/可维护性=高/可观测性=高
  - Pros: 开箱即用
  - Cons: 对仅使用 CLI 的用户是冗余依赖
- C) 插件化：定义 `ui_engine` 扩展点（entry_points）
  - Effect: 范围=架构/风险=中/质量=高/复杂度=中/工期=2d/成本=中/可维护性=最高/可观测性=高
  - Pros: 长期扩展性强（curses、urwid 等）
  - Cons: 初期过度设计

### 建议与权衡（Cycle 5）
- 建议：Q1→B，Q2→A，Q3→B，Q4→A，Q5→A，Q6→A，Q7→A，Q8→A
- 理由：
  1) 分屏职责清晰，便于测试与演进；
  2) 并行实施+开关保障，降低迁移风险；
  3) 以线程/后台任务接入，最小化对同步核心的侵入；
  4) 先保证功能对齐与键位一致性，降低学习成本；
  5) Textual Pilot 可自动化覆盖关键交互；
  6) 预计算+虚拟化保障大数据场景流畅；
  7) CLI 与环境变量双保险确保快速回退；
  8) 以 extras 引入依赖，兼顾轻量与可选性。
