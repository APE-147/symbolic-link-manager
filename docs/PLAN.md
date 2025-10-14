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
