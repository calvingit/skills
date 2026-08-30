---
name: prompt-optimizer
description: Improve or diagnose prompts for clearer, more reliable results.
---

# Prompt Optimizer

Turn rough or unreliable prompts into clear, usable prompts. Prefer the smallest prompt that will reliably produce the needed result.

## Core Standard

Optimize around five parts, using only the parts that matter:

1. **Goal** - Start with the result the user needs.
2. **Context** - Include only information or sources that could change the result.
3. **Output** - State format, audience, length, order, or level of detail when it matters.
4. **Boundaries** - Name the few things that must stay unchanged, must be avoided, or require confirmation.
5. **Check** - Add a final verification step for important, factual, tool-using, or high-impact work.

Do not force every prompt into a rigid template. Short prompts are acceptable when the task is simple.

## Workflow

1. Identify the intended result and how the user will use it.
2. Determine what context is actually needed; remove irrelevant background.
3. Choose the lightest useful structure:
   - direct rewrite for simple prompts
   - structured prompt for multi-step work
   - reusable template when the user wants repeat use
   - diagnosis plus rewrite when the user provides a failed output
4. Add only real boundaries: source limits, unchanged values, no external actions, no guessing, approval before publishing, or scope constraints.
5. Add a check when mistakes would create real cost: cite sources, flag missing info, verify action items, run tests, compare files, or report unverified assumptions.
6. Return a prompt the user can copy directly.

Ask at most one or two clarifying questions only when a missing decision changes the result and cannot be safely assumed. Otherwise, make the smallest reasonable assumption and state it outside the rewritten prompt.

## What To Fix

Prioritize issues that directly affect output quality:

- unclear or missing goal
- missing context that would change the answer
- too much context that distracts from the task
- vague output format or length
- missing audience or use case
- missing source/tool boundary
- conflicting instructions
- unverifiable success criteria
- over-control of process when only the result matters
- requests to guess facts, sources, APIs, files, or tool capabilities

Do not repeat the same diagnosis in different words.

## Construction Rules

- Start with the desired result, not a long list of steps.
- Use concrete actions instead of vague phrasing like "analyze carefully" or "make it better".
- Convert subjective quality words into observable criteria: sections, word count, fields, checks, examples, or exclusion rules.
- Keep approved facts, numbers, dates, budgets, names, and source limits explicit when they matter.
- For current facts, research, legal, medical, financial, product, pricing, or policy prompts, require current sources and links.
- For tool or agent workflows, define the task, allowed sources/tools, side-effect boundaries, and completion evidence.
- For code prompts, include behavior, relevant paths or reproduction steps, constraints, and verification commands.
- For image or UI prompts, include visible requirements plus behavior not shown by the image, such as states, validation, or interactions.
- Remove decorative constraints, repeated warnings, model-specific names, and "for later" scaffolding unless the user explicitly needs them.
- Flag missing information instead of inventing it.

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

## Quality Check

Before responding, confirm:

- The goal is visible near the top.
- Context is sufficient but not bloated.
- Output format is stable enough for the user's use case.
- Boundaries prevent real problems, not imaginary ones.
- Important work has a final check.
- Missing facts are marked or converted into assumptions.
- The rewritten prompt does not depend on a specific model name unless the user asked for that.
- The response itself is no longer than needed.

## References

Load these only when needed:

- `references/enhancement-modules.md` - optional rule blocks for research, structured output, code, tools, long tasks, and professional writing
