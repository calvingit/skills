# Engineering Skills 维护规范

本文只约束如何治理这套 Skills：什么时候新增、合并或删除，Kernel 怎样演进，改动后如何验证，以及如何做 Retro 和实验。单个 Skill 怎么用、Runtime 生命周期、项目配置和业务规则不在这里，分别见各 Skill、[职责与边界](engineering-responsibilities.md)、[调用关系](engineering-invocation.md)和[使用指南](engineering-skills.md)。

## 新增 Skill 的标准

Engineering Skills 处于收敛期：暂停新增全局工程 Skill（2026-10-16 Calvin 明确批准的 show-me 迁入和 visual-pr 新增除外），不新增通用编排层、Runtime 抽象或 CI（不添加 `.github/workflows`），优先修正已有职责、项目配置和工具入口。

只有真实任务证明现有职责无法承接某项能力时，才提出新增方案。新增的 Skill 须满足：

- 原子、独立：有自己的判断目标和停止点，单独安装也能使用，不依赖另一个 Skill 的内部细节。
- 通用：不绑定语言、框架或 Agent Runtime；项目实现细节、领域术语、ADR、Git 规则和测试约定由目标仓库维护。
- 不是项目知识：项目本地的验证入口属于项目，不等于增加全局 Skill。

## 合并、精简与删除

- 判断目标和停止点不同的 Skill 保留，不因检查同一份代码或测试就合并。
- 通过组合复用规则，不复制另一 Skill 的执行细节；各 Skill 不复制完整的流程路由表，只保留本 Skill 的硬性停止条件。
- 精简时不能静默删掉已确认的能力，例如自动记录 decisions、术语对齐和 ADR。
- 新增限制必须对应明确需求或已观察到的问题；通用常识、重复要求、分类教学和假设性防护不进入正文。
- 重复出现且可确定性判断的问题，先考虑用 script、schema、lint、test 或 metadata 约束，不继续往 SKILL.md 叠加提示词；只有需要上下文判断或跨 Runtime 解释的规则才写成文字。不要为了一次偶发输出引入新工具。
- 优先修正有问题的局部，不因一次输出不理想就重写整体流程，也不以行数作为质量指标。

## 上游适配

源自 Matt Pocock 的 Skill 以上游原版为基础，只添加确有需要的适配；自行设计的 Skill 不强行套用上游结构。改动前先核对原文，保留核心机制、关键术语和交互节奏，记录来源与适配理由。适配集中在项目约定、文档位置、必要的技能组合和 Runtime 能力差异。

现有适配记录：

- grilling 基于 [Matt 的原版](https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md)，保留 design tree、frontier、round 和每轮批量提出整个 frontier 的机制；本地增加快捷回复格式、通用事实调查、项目内决策记录，以及与 domain-modeling 组合写入术语和 ADR。尚未做行为对比验证。
- tdd 基于 [Matt 的原版](https://github.com/mattpocock/skills/blob/main/skills/engineering/tdd/SKILL.md)，保留行为测试与逐步反馈；2026-09-26 核对上游后，取消逐个测试边界的重复确认，技术测试边界不写入 SPEC，允许 Green 后局部重构，并要求预期值有独立依据。尚未替代真实项目中的长期效果评估。

## Kernel 演进

[Engineering Kernel](ENGINEERING_KERNEL.md) 只收录跨 Skill 的不变量。修改 Kernel 须有真实的不变量错误或缺口，并说明受影响的 Skill；不确定时先报告，不顺手改。Kernel 不代替项目契约、角色写入边界或强制门禁，也不能作为删减既有门禁的文字依据，门禁的改变须有行为证据。

## 文字约定

文档用自然的中文，避免 AI 腔、翻译腔和模板化表达（可用 `unslop` 检查）；SKILL.md 正文沿用各自现有语言。

## 验证

| 改动 | 方法 | 能证明什么 |
| --- | --- | --- |
| 任何文档或 Skill | `python3 scripts/check_repo.py`（本地链接与锚点、SKILL.md frontmatter、`agents/openai.yaml` 基本格式，再运行状态脚本测试）和 `git diff --check`；改动插件清单时运行 `claude plugin validate .` | 只证明格式和引用有效，不证明路由、约束强度或 Runtime 加载 |
| 状态脚本（ticket graph、事务、CLI、交付快照） | `python3 engineering/shared/check.py`，测试在 `engineering/shared/tests/` | 临时仓库上的图、CLI 和快照行为，不执行真实 Agent 生命周期 |
| 较大的流程改动：任务契约、路由、产物归属、验证判断 | 在隔离目录用当前候选 Skill 演练受影响的真实场景，检查实际决定、文件和观察 | 只覆盖演练过的场景 |
| 后端 Skill | 用受影响的后端场景做隔离演练 | 文本演练不等于真实数据库测试 |

按改动风险选择，不必每次跑全部。演练时记录候选（`HEAD` 加未提交改动）、实际命令、退出码、关键输出和覆盖缺口；只给执行者原始请求和输入，不附期望答案；验收用独立上下文。缺少前提（如 Python 3.10+、Git）时报告，不静默安装。

审阅文档不能证明 Runtime 生命周期、真实项目 GUI 质量或长期 token / 耗时改善；声称效果改善前，用相同任务、模型和上下文比较关键遗漏、无效追问、用户纠正和阅读负担。

## Retro 与实验

- 会话级系统性问题收集真实证据，只观察、诊断并路由给现有负责方；没有正式 retro Skill，也不自动进入交付流程。
- 收尾角色等流程调整，取得真实证据并经评审前，现有要求不变。
