# Retro 实验规范

用真实 Coding Agent session 判断是否需要独立的会话级反馈能力。当前只建立可重复实验，不新增正式 `retro` Skill，也不把复盘设为每次交付的强制阶段。观察、诊断、分类和路由在此完成；实际修改交给现有 owner，并遵守当前授权。

## 样本与输入

至少收集以下三类真实任务。当前尚未在此记录实际样本；测试 fixture、规则演练和对话摘要不能冒充真实 session。

| 样本 | 任务 | 重点观察 |
| --- | --- | --- |
| Session A | 长时间 Loop / ticket graph 任务 | 上下文压力、worker 启动、review/fix 循环、验证成本、状态转换 |
| Session B | 普通 quick implementation | 导航、测试选择、指令适用性、工具调用 |
| Session C | GUI / Web / App / E2E 任务 | 验证缺口、视觉证据、交互验证、环境准备 |

每份样本保留任务目标、候选 revision 与相关未提交 diff、Runtime/模型版本（可获取时）、实际 session/命令/报告的来源和可定位片段。注明缺失或裁剪部分，以及哪些资料仅推测被加载。耗时、调用数和错误须来自记录；不能从感觉估算成实测值。脱敏且只使用获准访问的资料，结果放在调用方指定的证据目录，不写入稳定 Profile 或产品快照。

## 检查与记录

按实际发生的事件检查下表，不要求每类都找到问题。

| 维度 | 检查问题 |
| --- | --- |
| Navigation | 是否反复寻找已存在的入口、误读目录或遗漏 authority？ |
| Verification | 是否选错验证层次、重复执行无新增价值的检查，或以不足证据声称通过？ |
| Deterministic guardrails | 是否存在可由 script / schema / lint / test 可靠阻止的重复错误？ |
| Agent instructions | 指令是否冲突、过时、无法执行或对当前任务没有实际作用？ |
| Tool economy | 无效调用、重复调查是否有可观察成本，是否已有更合适的工具？ |
| Context loading | 是否重复加载大段资料，遗漏必要上下文，或将临时事实混入长期规则？ |
| Information access | 是否把不可访问的信息当成事实，或缺少稳定文档入口？ |
| Runtime / orchestration | 是否有 worker 启动、等待、恢复、共享资源或调度问题？区分 Runtime 故障与 Skill 决策错误。 |

每个 finding 使用以下最小记录；相关片段可以链接，不复制整段 session：

- **发生了什么**：来源位置、当时目标、动作及结果。
- **实际代价或错误**：可观察的延误、重复工作、错误输出或证据缺口；未量化则明确说明。
- **是否可能复发**：支持复发判断的条件与其他样本；一次偶发不能写成稳定规律。
- **负责方与最小建议**：一个主要 owner，必要时列出相关 owner；没有合适 owner 时记录缺口，不自行创建 Skill。
- **确定性机制是否足够**：优先已有工具，说明何处仍需要判断，不为单次事件自动增建工具。
- **证据与反证**：可追溯材料、替代解释、不可见范围，以及如何验证建议有效。

按原始 session 先定位事件，再解释原因。分别记录已观察事实、推断和待验证假设；不要把结果不佳直接归因于提示词。单次业务 bug 由实现/审查处理，只有可解释的重复环境或流程问题才支持系统性改进。

## 路由与边界

| Finding | 当前 owner |
| --- | --- |
| AGENTS.md 组织和指令维护 | `engineering/improve-agents-md` |
| 上下文重复、冲突、无效指令 | `global/context-audit` |
| 验证方法、环境准备与证据能力 | `engineering/verification-setup` |
| Profile 或稳定导航 | `engineering/project-setup` |
| 可确定性检查的重复错误 | 仓库 tooling 维护者；涉及验证方法时组合 verification-setup |
| 领域术语与长期领域文档 | `engineering/domain-modeling` |
| 实现缺陷与不必要复杂度 | `engineering/code-review` / `engineering/simplify`，修复交给实现方 |
| 原生 worker 生命周期故障 | Runtime 维护者；保留复现，不在 Skill 内另建 Runtime |
| Loop 的范围、交接或交付判断 | `engineering/loop` 维护者，限定在已有职责 |

实验输出只给建议和路由，不自动编辑 AGENTS.md、构建 harness、修改 Profile 或重写 Skills。对已授权的后续实施，由负责方单独执行并验证；本实验的建议不是新的权限。

## 比较与解除 Freeze 条件

对同一原始 session，比较本实验与直接调用现有 audit 的结果，记录是否有额外的有效 finding、误报、调查成本和可执行路由。已获准的改进再通过后续同类真实任务观察复发情况；模型、任务或环境不同时注明比较限制，不能直接归因为 Skill 改进。

只有三类样本均有真实记录，且多次任务共同支持以下条件，才提出解除 Freeze 的建议：

1. 会话级 finding 有持续价值，能指出具体错误或成本。
2. 有效问题跨多个已有 Skill owner，单一 owner 难以完整承接观察。
3. 单独调用现有 audit 难以复现这些 finding，组合成本也有实际证据。
4. 结果能稳定路由为具体改进，而非泛泛建议。

样本不足、只有一次偶发问题、现有 audit 已能承接或收益无法验证时，继续使用已有能力。即使满足条件，也只提出正式 Skill 的建议，由维护者决定；未来职责仍限定为 observe / diagnose / classify / route。
