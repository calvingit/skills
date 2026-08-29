# Report Template

报告位置遵循目标仓库已有任务/报告约定；没有稳定约定且用户未指定位置时，先在当前会话输出，不擅自创建项目级目录规范。

```markdown
# Architecture Review — <scope>

## Summary
- Scope: <评审范围>
- Coverage: <已覆盖区域与 blind spots>
- Result: <critical/high/medium/low findings / no finding / needs more evidence>
- Top finding: <ID、主题、severity>
- Next step: <codebase-design / grilling / to-spec / simplify / observe>

## Review Basis
- Question: <本轮要回答的架构问题>
- Project authorities: <实际发现的 instructions、architecture docs、ADRs、rules>
- Project controls: <实际存在且相关的 checks；没有则写 none>
- External guidance: <实际使用的官方技术栈依据；没有则写 none>

## Architecture Map
- Entrypoints: <主要入口>
- Ownership boundaries: <相关 Module / package / layer>
- Dependency direction: <关键依赖关系>
- State / lifecycle owners: <关键状态与生命周期>

## Evidence
| Kind | Source | Observation | Status |
|---|---|---|---|
| code / call path / test / rule / history / command / official guidance | file:symbol / command / source | ... | Observed / Inferred / External guidance / Unknown |

## Findings

### A-001 — <finding> `[Critical | High | Medium | Low | Speculative]`

- Concern: <Boundary / Ownership / Dependency / State / ...>
- Evidence: <当前代码、关系、测试、规则或命令>
- Impact: <实际风险、变更扩散、维护成本或验证困难>
- Basis: <project rule / current architecture evidence / external guidance / design judgment>
- Recommendation direction: <目标架构结果，不写文件级实现步骤>
- Unknowns: <仍需决策或验证的事实>
- Counter-evidence / trade-off: <为什么现有设计可能合理，或已考虑但不足以否定 finding 的证据>

## Not Findings
- <被检查但 evidence 不支持的问题，以及反证>

## Next Step
- <用户选择 finding 后交给对应 skill；review-architecture 本身不实现>
```

若项目存在 lint、dependency check、architecture guard 或 baseline，可作为 Evidence 记录命令、退出状态和摘要；不要为了填充模板要求项目必须具备这些机制。
