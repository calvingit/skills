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

## Output

Return only the rewritten prompt when requested. Otherwise briefly explain material issues and provide the usable prompt. Read [references/output-patterns.md](references/output-patterns.md) when a structured template or failed-output diagnosis is useful.

## Quality Check

Check the result against the five-part Core Standard and resolve conflicting instructions. Mark missing facts or state assumptions; do not repeat the diagnosis or add unnecessary response sections.

## References

Load these only when needed:

- `references/enhancement-modules.md` - optional rule blocks for research, structured output, code, tools, long tasks, and professional writing
