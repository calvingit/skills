# Engineering Skills 维护说明

面向本仓库维护者。职责、调用关系和入口选择分别见[职责与边界](engineering-responsibilities.md)、[调用关系](engineering-invocation.md)和[使用指南](engineering-skills.md)。

## 收敛期约定

维护现有 Engineering Skills 的职责划分、产物写入范围和结论依据。暂不新增全局 Skill、通用编排层或 Runtime，优先组合已有能力和项目方法。项目本地验证入口属于项目知识，不等于增加全局 Skill。恢复新增前，需以真实任务说明现有职责无法承接的能力缺口。

## 设计原则

- 通用优先，项目实现细节、领域术语、ADR、Git 规则和测试约定由目标仓库维护。
- 每个 Skill 有明确的判断目标和停止点，可以围绕不同目标检查同一份代码或测试。
- 通过组合复用规则，不复制另一 Skill 的执行细节。各 Skill 不再复制完整的流程路由表，只保留本 Skill 的硬性停止条件。
- 能由确定性机制可靠保证的约束，不交给 Agent 记忆和判断。
- 以确认需求、代码、实际观察和独立报告为依据，不把自报或命令成功当成完成证明。
- Runtime 管理会话与 worker 生命周期，Engineering Skills 管理需求、设计、执行图和交付判断。

## 上游适配

对于源自 Matt Pocock 的 Skill，以上游原版为基础，只添加 Engineering Skills 确有需要的适配。自行设计的 Skill 不强行套用上游结构。

- 保留原版的核心机制、关键术语和交互节奏，改动前先核对原文，记录来源与适配理由。
- 适配集中在项目约定、文档位置、必要的技能组合及 Runtime 能力差异，不把下游流程说明塞进每个 Skill。
- 新增限制必须对应明确需求或已观察到的问题。通用常识、重复要求、分类教学和假设性防护不进入正文。
- 对重复出现且可确定性判断的问题，先考虑能否通过 script、schema、lint、test、validation 或 metadata 编码约束。结构化约束能够更可靠、更低成本地防止问题时，不要继续往 SKILL.md 叠加提示词。只有需要上下文判断、权衡或跨 Runtime 通用解释的规则才保留为 prose。不要为了消除一次偶发输出就引入新的工具或自动化机制。
- 通过组合复用已有规则，不复制另一 Skill 的细节，精简时也不能静默删掉已确认的能力，例如自动记录 decisions、术语对齐和 ADR。
- 优先修正有问题的局部，不要因一次输出不理想反复重写整体流程，也不以行数作为质量指标。
- 声称效果改善前，用相同任务、模型和上下文比较关键遗漏、无效追问、用户纠正及阅读负担。静态检查只能证明格式与规则一致，不能证明实际效果更好。

当前 grilling 基于 [Matt 的原版](https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md)，保留 design tree、frontier 和 round，以及每轮批量提出整个 frontier 的机制。本地适配包括紧凑的快捷回复格式、通用事实调查、项目内决策记录，以及与 domain-modeling 组合写入术语和 ADR。尚未完成行为对比验证。

TDD 基于 [Matt 的原版](https://github.com/mattpocock/skills/blob/main/skills/engineering/tdd/SKILL.md)适配，保留行为测试与逐步反馈。2026-09-26 核对上游后，按本仓库已确认的职责调整：取消逐个测试边界的重复确认，技术测试边界不写入 SPEC；允许 Green 后按需做局部重构；判断预期值的独立依据，不把字面量视为天然可信，也不把公式视为天然无效。较大设计变更仍交回调用方处理。这些调整不替代真实项目中的长期效果评估。

会话级系统性问题先按 [Retro 实验规范](../../.agents/skills/verify-engineering/references/retro-evaluation.md)收集真实证据，只观察、诊断并路由给现有 owner；没有新增正式 retro Skill，也不自动进入交付流程。

## 验证边界

图、attempt、事务和交付快照由现有 `python3 engineering/shared/check.py` 检查，Profile 迁移、按需读取及验收证据选择另用隔离任务演练。审阅文档不能证明 Runtime 生命周期、真实项目 GUI 质量、长期 token 或耗时改善，这些效果需后续真实任务记录支持。

本仓库的检查与行为评估入口是 [verify-engineering](../../.agents/skills/verify-engineering/SKILL.md)，静态检查和状态脚本测试只能支持各自覆盖范围的结论。
