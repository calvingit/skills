# Simplification Investigation

用于 Survey、Broad scope，或存在动态加载、外部消费者、持久化兼容等不确定性的 Change。

## Evidence ladder

不要把 smell 或静态搜索结果当成删除授权。按证据强度推进：

1. **Smell**：看起来存在复杂度、重复或过度抽象。
2. **Static lead**：搜索、lint、compiler 或 analyzer 显示少量或无使用。
3. **Consumer map**：仓库内命中已分类，相关 caller/callee 已阅读。
4. **Contract proof**：动态加载、外部使用、持久化、兼容性、ownership 和当前设计理由已确认或明确列为未知。
5. **Behavior proof**：存在一个能暴露错误删除的 decisive check，并知道失败后的恢复路径。

高置信度 Change 通常至少需要 consumer map、contract proof 和 behavior proof。

## Consumer classification

对命中结果分类，不只统计引用数量：

- **Runtime**：生产代码、真实 entrypoint、运行配置、migration、loader、deployment 或其他实际执行路径。
- **Support-only**：tests、纯说明 docs、snapshots、已确认仅用于示例的 examples、generated expectations。
- **Uncertain**：public exports、fixtures、plugin registrations、reflection、lazy imports、string dispatch、manifests、generated code、可能被外部 package 使用的接口。

存在未解决的 dynamic / external consumer 时，不得把候选升级为高置信度删除。

## Coverage

Focused：围绕用户指定的 subsystem、symbol、state machine、dependency 或 suspected duplication 完整追踪其 ownership 和 contract，不主动扩张。

Broad：先按责任域建立 coverage map，再排名候选。至少考虑与当前仓库相关的 entrypoints、runtime control、public APIs/config、state/lifecycle、persistence/compatibility、plugins/DI/reflection/codegen、background workers、packages/adapters/tests/docs。无法检查的区域记录为 blind spot。

不要因为找到第一个可删点就结束 Broad survey。

## History as evidence

当存在历史设计、兼容逻辑或原因不明的抽象时，使用 git history、blame、PR、issue、ADR、RFC 或 comments 回答：

- 它最初为哪个 failure、requirement 或 future plan 引入？
- 该条件现在是否仍成立？
- 当前哪个 artifact 或 owner 仍在维护这个决策？
- 删除后什么能力会变得昂贵或不可恢复？

“很久没改”或“搜索不到调用”都只能作为发现线索。

## Survey output

Survey 不修改代码。报告：coverage、已证明并排序的候选、重要的 rejected / unresolved 候选，以及每个不确定项还缺少的具体事实。

排名时分别考虑 confidence、benefit、blast radius、reversibility 和 validation strength；不要按删除行数或候选数量排名。
