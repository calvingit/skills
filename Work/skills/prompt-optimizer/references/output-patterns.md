# Output patterns

## Default Skeleton

Use this only when structure helps; delete unused sections.

```markdown
# Goal
[What to produce, decide, explain, change, or verify.]

# Context
[Only the sources, facts, audience, examples, files, screenshots, or constraints that change the result.]

# Requirements
- [Concrete requirement]
- [Concrete requirement]

# Boundaries
- [What must stay unchanged or out of scope]
- [What not to guess, send, publish, modify, or spend]

# Output
[Format, order, length, tone, table/schema, or file requirements.]

# Final Check
- [Verification, source check, consistency check, owner/due-date check, test command, or assumption report.]
```

## Output Modes

Use one mode. Do not add extra sections when the user asks for only the final prompt.

### Final Prompt Only

When the user asks for "只输出最终版本", "直接给 prompt", or similar, return only the rewritten prompt.

### Failed Output Provided

```markdown
## 问题诊断

| 问题 | 证据 | 修复方式 |
|---|---|---|
| [问题] | [来自原 prompt 或失败输出的具体表现] | [对应改法] |

## 最小修复版本

[Smallest prompt that fixes the failure.]

## 完整优化版本

[Reusable or more structured prompt, only if useful.]
```

### Normal Case

```markdown
## 主要问题

- [Only the issues that materially affect the result.]

## 优化后的提示词

[Copy-ready prompt.]

## 可选增强

- [Only if a genuinely useful optional addition exists; otherwise omit this section.]
```
