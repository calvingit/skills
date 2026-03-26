# Claude-Specific Prompt Engineering Notes

This file covers behaviors, defaults, and deprecated patterns specific to **Anthropic Claude models**.
Read this in addition to `best-practices.md` whenever the target model is Claude.

Source: Anthropic official documentation (Claude 4.6 / Sonnet 4.6 / Haiku 4.5)

---

## Table of Contents
1. Model Family Overview
2. Deprecated Patterns (Claude 4.6+)
3. Proactivity & Anti-Laziness Calibration
4. Tool Use Defaults
5. Thinking & Reasoning Modes
6. Agentic System Specifics
7. Migration Checklist (from older Claude versions)

---

## 1. Model Family Overview

| Model | Best For | Default Effort |
|---|---|---|
| Claude Opus 4.6 | Hardest long-horizon tasks, deep research, large-scale code migration | Adaptive (high) |
| Claude Sonnet 4.6 | Fast turnaround, cost efficiency, most production workloads | High (default) — consider setting `medium` or `low` |
| Claude Haiku 4.5 | High-volume, latency-sensitive, simple classification/extraction | — |

**Sonnet 4.6 note:** Default effort is `high`, which can increase latency. For most applications set `effort: "medium"`. For high-volume or latency-sensitive workloads, use `effort: "low"`.

---

## 2. Deprecated Patterns (Claude 4.6+)

### ⚠️ Assistant Prefill — DEPRECATED

Prefilled responses on the last assistant turn are no longer supported in Claude 4.6 models.

**Old pattern (do not use with Claude 4.6+):**
```python
messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": user_message},
    {"role": "assistant", "content": "Here is the JSON result:"}  # ← deprecated
]
```

**Migration:** Move format constraints to `<output_format>` in the system prompt instead.
```
<output_format>
Respond with a valid JSON object only. No explanation, no markdown fences, no preamble.
{"source_language": "...", "answer": "..."}
</output_format>
```

> Note: Adding assistant messages *earlier* in the conversation (not as the last turn) is still supported.

---

## 3. Proactivity & Anti-Laziness Calibration

Claude Opus 4.6 and Sonnet 4.6 are significantly more proactive than previous models. Instructions designed to prevent undertriggering in older Claude versions will cause **overtriggering** in these models.

### Dial Back Aggressive Language

| Old pattern (overtriggers on 4.6) | Replacement |
|---|---|
| `CRITICAL: You MUST always use this tool` | `Use this tool when [condition]` |
| `NEVER skip this step under any circumstances` | `Always complete this step before responding` |
| `If in doubt, use [tool]` | `Use [tool] when [specific trigger]` |
| `Default to using [tool]` | `Use [tool] when it would enhance your understanding` |

### When to Keep Strong Language
Strong emphasis is still appropriate for:
- **Safety-critical rules** where any deviation causes serious harm
- **Format contracts** where a downstream parser will break on deviation
- **Explicit user-confirmed failure modes** from real bad cases

---

## 4. Tool Use Defaults

### Explicit Trigger Conditions
Claude 4.6 models are trained for precise instruction following. Use explicit triggers rather than permissive framing:
- "Can you suggest changes?" → Claude may suggest rather than implement
- "Use the edit tool to apply this change." → Claude will act

To make Claude proactive about tool use by default:
> "Prefer taking action over describing what action to take."

To make Claude more conservative:
> "Describe what you would do before taking any action. Only proceed if I confirm."

### Parallel Tool Calling
Claude 4.6 models execute tools in parallel by default and have a high success rate without explicit instruction.

- **Boost to ~100%:** "When multiple tools could be called, call them all in a single turn."
- **Reduce parallelism:** "Call tools one at a time, in sequence."

---

## 5. Thinking & Reasoning Modes

### Adaptive Thinking (Claude Opus 4.6)
- Uses `thinking: {type: "adaptive"}` — Claude decides when and how much to think.
- Calibrated by `effort` parameter and query complexity.
- Internal evals show adaptive thinking outperforms manual extended thinking.
- If Claude is thinking more than needed with large system prompts, add: "Only engage extended thinking for genuinely complex multi-step problems."

### Extended Thinking (Claude Sonnet 4.6)
- Supports both adaptive and manual extended thinking with interleaved mode.
- Recommended thinking budget: ~16k tokens (provides headroom without runaway usage).
- For coding/agentic workloads: start at `medium` effort.
- For chat/content generation: start at `low` effort with thinking.

### Manual Chain-of-Thought (Thinking Disabled)
- Use `<thinking>` and `<answer>` tags to separate reasoning from final output.
- Use multishot examples with `<thinking>` blocks to demonstrate reasoning patterns.
- **Avoid the word "think"** when extended thinking is disabled in Claude Opus 4.5 — it's sensitive to the word and variants. Use "consider", "evaluate", "reason through" instead.

---

## 6. Agentic System Specifics

### Subagent Orchestration
Claude Opus 4.6 and Sonnet 4.6 can recognize when to delegate to subagents without explicit instruction. However, **Opus 4.6 has a strong tendency to spawn subagents** even when a simpler direct approach would suffice (e.g., spawning a subagent for a grep call).

To prevent over-orchestration:
> "Use subagents only when tasks are genuinely parallelizable or require specialized capabilities. For simple lookups or single-file operations, proceed directly."

### Long-Horizon State Tracking
- Claude 4.6 models maintain orientation across extended sessions.
- For multi-context-window tasks: use `tests.json` for structured test state, `progress.txt` for notes, git for history.
- Claude 4.6 models are effective at discovering state from the filesystem — consider starting fresh context windows from filesystem state rather than context compaction.

### Context Awareness
Claude 4.6 and 4.5 models track their remaining context window (token budget) throughout a conversation. If you use a harness that compacts context or saves to external files, add this to your prompt so Claude behaves accordingly:
> "This session uses context compaction. Continue working without wrapping up when the context limit approaches."

### Safety for Irreversible Actions
Without guidance, Claude Opus 4.6 may take irreversible actions (delete files, force-push, post to external services). Add explicit confirmation prompts if needed:
> "Before taking any action that cannot be undone, describe what you're about to do and ask for confirmation."

---

## 7. Migration Checklist (from older Claude versions)

When migrating prompts from Claude 2.x / Claude 3.x / Sonnet 4.5 to Claude 4.6 models:

- [ ] **Remove assistant prefill** on the last turn — migrate format constraints to system prompt `<output_format>` block
- [ ] **Audit aggressive language** — search for MUST, NEVER, ALWAYS, CRITICAL and evaluate whether they're still needed or will overtrigger
- [ ] **Remove over-prompting for tool use** — "If in doubt, use X" → remove or add a specific condition
- [ ] **Update thinking configuration** — replace `thinking: {type: "enabled", budget_tokens: N}` with `thinking: {type: "adaptive"}` + `effort` parameter
- [ ] **Set explicit effort level for Sonnet 4.6** — default is `high`; set `medium` for most applications, `low` for high-volume
- [ ] **Request features explicitly** — animations, interactive elements, and detailed formatting must be requested; don't assume the model will add polish
- [ ] **Test subagent behavior** — if using Opus 4.6, check whether subagent spawning is appropriate for your workload
