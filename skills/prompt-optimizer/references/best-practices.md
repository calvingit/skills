# Universal Prompt Engineering Best Practices

These principles apply to all large language models regardless of provider (Claude, GPT, Gemini, DeepSeek, Mistral, etc.).

For model-specific behavior, see the relevant reference file (e.g., `claude-best-practices.md`).

---

## Table of Contents
1. Clarity & Directness
2. Context & Motivation
3. Examples (Few-Shot Prompting)
4. Structure with XML Tags
5. Role Assignment
6. Output Format Control
7. Long Context Prompting
8. Failure Mode Coverage
9. Agentic & Tool-Use Prompts
10. Iterating on Prompts

---

## 1. Clarity & Directness

**State the task explicitly.**
Do not rely on the model to infer your intent from vague instructions. Describe exactly what you want produced.

**Use positive directives, not prohibitions.**
- Weak: "Do not use bullet points."
- Strong: "Write your response as flowing prose paragraphs."

Models respond more reliably to instructions about what to do than what to avoid.

**Use sequential numbered steps when order matters.**
If a task has multiple steps, number them explicitly. "First X, then Y, finally Z" is clearer than a flat list.

**Golden rule:** Show your prompt to a colleague with no context. If they'd be confused, the model will be too.

---

## 2. Context & Motivation

**Explain why critical rules exist.**
Models generalize from explanations, not just rules. "Never leave Chinese words in a Thai translation because it breaks the buyer's reading experience" outperforms "Never leave Chinese words in output."

**Provide relevant background.**
Who are the users? What is the downstream use of the output? What does success look like?

---

## 3. Examples (Few-Shot Prompting)

Examples are one of the most reliable ways to control output format, tone, and behavior.

**Include 3–5 examples for best results.**

**Make examples:**
- **Relevant** — Mirror real use cases as closely as possible.
- **Diverse** — Cover edge cases, boundary conditions, and known failure modes.
- **Structured** — Wrap in `<examples>` / `<example>` tags.

**Prioritize bad cases as examples.**
Known failure inputs with the correct output are more effective than abstract rules describing the failure.

**Example format:**
```xml
<examples>
  <example>
    <input>[realistic input]</input>
    <output>[correct output]</output>
  </example>
  <example>
    <input>[edge case input]</input>
    <output>[correct edge case output]</output>
  </example>
</examples>
```

---

## 4. Structure with XML Tags

XML tags eliminate ambiguity when a prompt mixes instructions, context, examples, and variable input.

**Wrap each content type in a dedicated tag:**
- `<instructions>` — What the model must do
- `<context>` — Background information
- `<examples>` — Few-shot demonstrations
- `<input>` — The variable/user-supplied content
- `<output_format>` — How the response must be structured

**Use consistent, descriptive tag names** across your prompt system.

**Nest tags for hierarchical content:**
```xml
<documents>
  <document index="1">
    <source>report.pdf</source>
    <content>...</content>
  </document>
</documents>
```

---

## 5. Role Assignment

A one-sentence role at the top of the system prompt focuses behavior and tone.

**Pattern:** "You are a [role] specializing in [domain]."

- "You are a professional translation engine for cross-border e-commerce customer service."
- "You are a senior software engineer reviewing code for production readiness."
- "You are a concise JSON extraction engine — you output only valid JSON, nothing else."

---

## 6. Output Format Control

**Specify the exact format.** Don't leave the model to infer whether you want JSON, markdown, plain text, or XML.

**For JSON output:**
- Provide an exact schema with field names and types.
- Show a concrete example in `<output_format>` tags.
- State explicitly: "Respond with a valid JSON object only. No explanation, no markdown fences, no extra text."

**For structured documents:**
- Show a template with exact section headers.

**Match prompt formatting to desired output formatting.**
If your prompt uses markdown, the output is more likely to use markdown. Remove formatting from the prompt if you want plain-text output.

---

## 7. Long Context Prompting (20k+ tokens)

**Put data at the top, query at the bottom.**
Place documents and reference material above the query and instructions. This improves response quality on complex multi-document inputs.

**Structure multiple documents with XML:**
```xml
<documents>
  <document index="1">
    <source>filename.pdf</source>
    <content>...</content>
  </document>
</documents>
```

**Ask the model to quote before answering.**
"First quote the relevant passage(s) from the document, then answer." Grounds the response in actual content.

---

## 8. Failure Mode Coverage

**Write rules that address your actual failures, not hypothetical ones.**

**Partial-execution failures** (model skips part of the input):
- Name the skipped element explicitly in a rule.
- Add a WRONG / CORRECT contrast example using the real failure case.

**Format failures** (right content, wrong format):
- Add an explicit output format example.
- Restate the format requirement close to the output block.

**Hallucination failures** (model invents information):
- Ask the model to quote source material before answering.
- Add: "If the information is not present in [source], say so rather than inferring."

**Ignored rule failures** (model knows the rule but doesn't apply it):
- Move the rule closer to the relevant input.
- Add a few-shot example demonstrating the rule.
- Explain *why* the rule exists.

---

## 9. Agentic & Tool-Use Prompts

**Be explicit about when to use tools.**
Permissive framing ("you can use X if needed") causes undertriggering. Explicit triggers ("use X when Y condition is true") are more reliable.

**State when NOT to use tools.**
"Answer directly without calling any tool when the query is a simple definition or does not require current information."

**For multi-step agent tasks:**
- Define explicit success criteria.
- Specify error handling: retry, ask for clarification, or fail with a message.
- For irreversible actions: require confirmation before execution.

---

## 10. Iterating on Prompts

**Start with bad cases, not abstract rewrites.**
The fastest improvement comes from fixing specific failures.

**Change one thing at a time.**
Modify one element per test so you can attribute any change to that edit.

**Test on diverse, real-distribution inputs.**
Including edge cases and adversarial inputs.

**Ask the model to evaluate your own prompt.**
"What cases would this prompt handle poorly? What rules are ambiguous?" Models are effective at identifying their own confusion.
