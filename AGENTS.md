# Repository guidance

Engineering Skills 当前处于收敛期：暂停新增全局工程 Skill，优先修正已有职责、项目配置和工具入口。只有真实任务证明存在无法承接的能力缺口时，再提出新增方案。

维护相关 Skill 时，按需读取 [职责与边界](docs/engineering-responsibilities.md)，修改 Profile 时读取 [配置约定](engineering/project-setup/references/profile.md)，普通修改不要求预读全部 Skills 或建立完整 SPEC / tickets。

涉及跨 Skill 交接、任务边界或路由时，按需读取 [任务契约](engineering/shared/task-contract.md) 和 [流程选择](engineering/shared/workflow-policy.md)。本仓库验证方法见 [.agents/skills/verify-engineering/SKILL.md](.agents/skills/verify-engineering/SKILL.md)，只加载当前改动需要的检查。

Skill 负责工程判断与产物，Runtime 负责会话和 worker 生命周期。保留确认需求、独立验收与状态约束，不复制另一角色的执行协议。

工程状态脚本的检查入口是 `python3 engineering/shared/check.py`，它只验证图、事务、CLI 和快照，不能代替 Skill 行为、GUI 或 Runtime 验证。修改文档时检查引用、元数据和 `git diff --check`，并按实际风险选择必要的行为演练。
