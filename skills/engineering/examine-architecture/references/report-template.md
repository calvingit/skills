# Report Template

写入按 `to-spec` skill 任务目录规则确定的稳定位置（无现成任务目录时先创建），文件名为 `architecture-exam-<timestamp>.md`；不要写入操作系统临时目录，跨会话把报告路径和 candidate ID 交给后续流程时依赖该路径可读。报告是调查工作产物，不进入 living spec；只有用户明确要求归档时才移动到长期位置。

```markdown
# Architecture Exam — <scope>

## Summary
- Scope：<调查范围与未覆盖部分>
- Result：<top candidate / no finding / needs more evidence>
- Top candidate：<ID、主题和 recommendation strength>
- Next step：<转 to-spec、继续调查、观察或不处理>

## Scope and Context
- Question：<本轮要回答的架构问题>
- Success criteria：<什么证据足以回答>
- Current authorities：<实际发现的 instructions、architecture docs、ADRs、glossary>
- Project controls：<实际存在且与范围相关的 checks；没有则写 none>

## Evidence
| Kind | Source | Observation | Status |
|---|---|---|---|
| code / call path / test / history / command | file:symbol 或 command | ... | Observed / Inferred / Unknown |

## Candidate Survey
| ID | Hypothesis | Lenses | Evidence strength | Disposition |
|---|---|---|---|---|
| A-001 | ... | Ownership / Depth / ... | strong / partial / weak | finding / not finding / investigate |

## Findings

### A-001 — <candidate name> `[Strong | Worth exploring | Speculative]`

- Evidence：<当前代码、关系、测试或命令>
- Friction：<理解成本、变更扩散、状态风险或测试困难>
- Desired outcome：<架构结果，不写具体 Interface 或文件级实现步骤>
- Unknowns：<仍需决策或验证的内容>
- Non-goals：<本候选不解决什么>

## Not Findings
- <被检查但当前 evidence 不支持的 hypothesis，以及反证>

## Next Step
- <让用户选择 candidate；选中后把报告路径和 ID 交给 to-spec skill>
```

如果项目确实存在 lint、dependency check、architecture guard 或 baseline，可把它们作为 Evidence 行记录命令、退出状态和摘要；不要为填充模板而要求项目必须具备这些机制。
