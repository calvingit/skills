# 项目验证方法使用示例

执行规则见 [Verification Setup](../SKILL.md)，本地方法应包含的内容见 [harness 契约](project-harness.md)，配置入口与迁移见 [Profile 约定](../../project-setup/references/profile.md)。已有文档、脚本或本地 Skill 足够时直接使用，需要建立可重复的方法入口时再运行 setup。

## 只盘点、不执行

- `使用 verification-setup 盘点这个仓库现有的验证方法，列出来源、命令、前置条件、能证明的范围和限制，不创建 Skill，也不运行。`

默认只交一份报告，不改项目文件，每项都标明“依据配置发现，未执行”。调用方明确授权时才更新已有 Verification 摘要，摘要只写导航信息，不抄完整命令。已有说明时只补缺项，不复制命令，不新增入口。没有说明且只要求盘点时，直接报告即可，不必新建 Profile 或独立的能力清单文件。

## 首次建立与增量维护

- 首次建立：`使用 verification-setup 分析这个仓库，复用已有验证工具，为当前产品建立项目本地验证 Skill，并实际跑通一条代表性路径。`
- 更新现有方法：`使用 verification-setup 更新 API 的验证入口，检查启动命令和测试数据隔离方式，保留现有 Web 验证方法。`
- 多端项目：`检查 mobile、web 和 api 的验证入口，以及登录流程跨端的证据缺口。只在执行方法不同的地方拆分 Skill。`

默认位置是 `.agents/skills/verify-<surface>/`，已有项目约定优先。共用执行方法时使用同一个 Skill，方法不同时按需拆分，通过简短导航定位各端和跨端路径，具体命令只在对应方法中维护。当前任务的 AC 对应关系留在会话或任务记录中，Profile 只维护稳定入口和能力摘要。

## 判断覆盖

例如任务需要观察原生权限操作，而仓库只有组件测试，就应保留原生流程的证据缺口。发现 Flutter 或 Web 不等于获准安装 Patrol、Playwright 或修改 CI，必要的依赖、测试与产品变更交回实现方。

报告区分已写入的方法、实际试运行的路径，以及已接受且适用于当前候选的证据。环境不可用或执行失败时，受影响的方法保持明确标注的草稿，不能用另一个方法通过代替。具体试运行和清理要求由 Skill 与 harness 契约维护，当前任务验收由 [verify](../../verify/SKILL.md) 判断。

## 设计来源

借鉴 pstack 的 [create-verification-skill](https://github.com/cursor/plugins/blob/main/pstack/skills/create-verification-skill/SKILL.md)：先从仓库查明运行、驱动、观察和隔离方法，生成本地技能后实际试运行，并在清理后保留证据。本仓库将创建和维护合在一个入口，沿用 `.agents/skills` 和已有 Profile，支持多端导航，保留全局 `verify` 的独立证据判断，不强制工具或测试层级。
