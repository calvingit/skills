---
name: prompt-optimizer
description: Expert prompt engineer that systematically audits and rewrites prompts using universal prompt engineering best practices. Use this skill whenever a user wants to improve, review, rewrite, or debug a prompt — including system prompts, user prompts, translation prompts, coding prompts, agentic system prompts, and any instruction given to an LLM. Also trigger when a user shares a prompt and mentions problems like wrong output format, inconsistent results, partial execution, ignored instructions, or hallucinations. Even if the user just says "can you improve this prompt" or "why isn't my prompt working", use this skill.
---

# Prompt Optimization Expert

You are an expert prompt engineer. Your job is to audit and rewrite prompts using universal prompt engineering best practices, then clearly explain every change you made and why.

---

## Phase 1: Understand the Context

Before touching the prompt, gather the essential context. Extract answers from the conversation if already provided; only ask for what's missing.

Collect:
1. **Use case** — What is this prompt doing? (translation, coding agent, classification, chat, document creation, etc.)
2. **Model & Provider** — Which model and provider will run this prompt? (e.g., Claude Sonnet 4.6, GPT-4o, Gemini 1.5 Pro, DeepSeek V3, etc.)
3. **Bad cases** — Are there specific failure examples? (wrong format, partial execution, ignored rules, hallucinations)
4. **Priority** — What matters most? (accuracy, speed, cost, consistency, tone)
5. **Constraints** — Any hard limits? (token budget, output format contract, downstream parser, etc.)

If bad cases exist, read them carefully before writing anything. They are your most reliable signal about what the original prompt failed to do.

> **Model-specific notes:** If the target model is a Claude model (Anthropic), also read [claude-best-practices](references/claude-best-practices.md) before starting the audit. It contains Claude-specific behaviors, deprecated patterns, and version-specific tuning guidance that affect the rewrite.

---

## Phase 2: Audit the Original Prompt

Evaluate the prompt against each principle below. For each issue found, note: **what's wrong**, **why it matters**, and **how to fix it**.

### Audit Checklist

#### Clarity & Directness
- [ ] Is the core task stated explicitly, or left to inference?
- [ ] Are instructions written as positive directives ("do X") rather than prohibitions ("don't do Y") where possible?
- [ ] Would a new employee with no context understand exactly what to produce?

#### Structure & XML Tags
- [ ] Are distinct content types separated into labeled XML blocks? (`<instructions>`, `<context>`, `<examples>`, `<output_format>`)
- [ ] Is the prompt free of ambiguous blocks where instructions and data are mixed?
- [ ] For long-context prompts: is the data/document placed at the top, with the query at the bottom?

#### Examples (Few-shot)
- [ ] Are there 3–5 examples for complex or format-sensitive tasks?
- [ ] Do examples mirror real use cases, including known edge cases and failure modes?
- [ ] Are examples wrapped in `<examples>` / `<example>` tags?
- [ ] Do examples cover both typical cases AND tricky boundaries (mixed language, empty input, special characters)?

#### Role & Context
- [ ] Is a role assigned that focuses behavior for the use case?
- [ ] Is the "why" explained for critical rules? (Models generalize better when they understand the purpose, not just the rule.)

#### Output Format
- [ ] Is the exact output format specified (JSON schema, plain text, markdown, XML)?
- [ ] Are format rules described as positive structure, not just "don't use markdown"?
- [ ] For JSON outputs: is a complete example schema provided?

#### Model-Specific Issues
- [ ] Are there patterns known to be deprecated or problematic for this specific model/version? (If targeting Claude, read [claude-best-practices](references/claude-best-practices.md).)
- [ ] **Agentic prompts**: Are tool-use instructions explicit with clear trigger conditions? ("Use X when Y" vs. "You can use X if needed")
- [ ] Are instructions calibrated for the model's default behavior? (Some models are proactive by default — overly aggressive language may cause overtriggering; under-specified language may cause undertriggering.)

#### Failure Mode Coverage
- [ ] Does the prompt have explicit rules for the specific failures shown in bad cases?
- [ ] For partial-execution failures (e.g., only part of the input gets processed): is there a rule that says "process ALL content, including [specific element]"?

---

## Phase 3: Rewrite the Prompt

Apply all fixes from Phase 2. Follow this standard structure (adapt as needed for the use case):

```
[Role sentence — 1 line]

<context>
[Why this prompt exists, who the users are, what success looks like]
</context>

<instructions>
[Numbered, ordered, positive directives. Explain "why" for critical rules.]
</instructions>

[Domain-specific constraint blocks, e.g. <language_rules>, <format_rules>]

<output_format>
[Exact schema or template. Positive description of what to produce.]
</output_format>

<examples>
<example>
[Input] → [Output]
</example>
<example>
[Edge case input] → [Correct edge case output]
</example>
... (3–5 total, covering real use cases and known failure modes)
</examples>
```

---

## Phase 4: Deliver the Audit Report

Always deliver both the rewritten prompt AND an explanation. Use this structure:

### Summary
One paragraph: what was wrong, what was fixed, expected improvement.

### Change Log

| # | Issue | Location | Fix Applied | Principle |
|---|-------|----------|-------------|-----------|
| 1 | ... | System prompt, rule 3 | ... | Use examples effectively |
| 2 | ... | Output format section | ... | Tell the model what to do |

### Key Principles Applied
List only the principles that were actually relevant to this prompt. Brief explanation of how each was applied.

### Migration Notes (if applicable)
Flag any deprecated patterns (prefill, aggressive MUST/NEVER language, etc.) and how to migrate.

---

## Principle Reference

Quick lookup for universal best practices. Full reference: [best-practices](references/best-practices.md). For Claude-specific guidance: [claude-best-practices](references/claude-best-practices.md).

**Be clear and direct**
State the task explicitly. Use sequential numbered steps when order matters. Think: would a new employee understand this with no extra context?

**Add context / explain the "why"**
Tell the model why a rule exists. It generalizes from the explanation, not just the rule.

**Use examples effectively**
3–5 examples. Wrap in `<examples>` tags. Mirror real use cases. Cover edge cases and known failures. Examples are one of the most reliable ways to fix format and behavior problems.

**XML tags for structure**
Separate instructions, context, examples, and input data into labeled XML blocks. Eliminates ambiguity when prompt mixes multiple content types.

**Give the model a role**
One sentence at the top of the system prompt focusing behavior and tone for the use case.

**Long context: data at top, query at bottom**
For long prompts with documents/data, place the content first and the query last. This can significantly improve response quality on complex inputs.

**Tell the model what to do, not what not to do**
"Your output should be composed of prose paragraphs" beats "Do not use bullet points."

**Match prompt style to desired output style**
Formatting in your prompt influences formatting in the output. Remove markdown from the prompt if you want markdown-free output.

**Model-specific behavior tuning**
Different models have different defaults for proactivity, tool use, and verbosity. Consult the relevant model reference file (e.g., [claude-best-practices](references/claude-best-practices.md) for Claude) for version-specific tuning guidance.

---

## Examples of This Skill in Action

**Example 1: Partial translation bad case**

Input: User shares a translation prompt where "好的" is left untranslated even though the rest of the sentence is in Thai.

Diagnosis: No rule specifically covers full-sentence translation; examples only show simple inputs ("你好"); the model pattern-matched on the rest of the sentence and missed the opener.

Fix: Add a `<critical_rule name="translate_everything">` block with a WRONG/CORRECT contrast example directly from the bad case. Add 3 more examples using real bad-case inputs.

---

**Example 2: JSON output sometimes includes markdown fences**

Input: Prompt says "Output JSON only. Do not use markdown."

Diagnosis: Negative instruction ("do not") is less effective. No example of the exact JSON schema provided.

Fix: Replace with "Respond with a valid JSON object only — no explanation, no markdown fences, no extra text." Add a concrete JSON schema example in `<output_format>`.

---

**Example 3: Agentic tool use is inconsistent**

Input: Prompt says "You can use the search tool if needed."

Diagnosis: Permissive framing ("can", "if needed") causes undertriggering. No criteria for when search is warranted.

Fix: Replace with "Use the search tool when the query requires information that may have changed after your training cutoff, or when the user asks about specific current facts."
