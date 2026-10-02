---
name: explain-that
description: Explain a selected term, sentence, decision, or approach from the previous Agent response, or restate that entire response in plain language when the user asks for simpler wording without selecting a specific part. Preserve conclusions, conditions, scope, and uncertainty.
---

# explain-that

Help the user understand the previous response with less jargon and only the background needed for the current conversation.

## Resolve the target

- If the user selects text or names a term, sentence, decision, or approach, explain that part. Do not restate the entire response unless requested.
- If the user explicitly asks to simplify the whole response, or asks for simpler wording without identifying a part, restate the entire previous response.
- Follow an explicit target over inferred selection. Ask only when ambiguity would materially change the explanation.

## Explain a selected part

- Start with its meaning in the current conversation, rather than a generic definition.
- Explain its role in the answer and add a small, relevant example only when useful.
- Explain recorded reasons for a decision when available; label inferred reasons as inference. Do not invent rationale or turn this into a new design investigation.
- Keep surrounding context only as far as needed to understand the selected part.

## Restate the entire response

- Rewrite the whole answer more simply and concisely, preserving each distinct conclusion, important fact, condition, scope limit, caveat, and uncertainty.
- Remove unnecessary jargon, repetition, and implementation detail. Keep details that affect the user's judgement or next action.
- Default to an experienced developer's level unless the user requests an introductory explanation. Do not turn the answer into a lesson or explain only one part.

## Shared boundaries

- Preserve technical meaning and certainty. Do not strengthen claims, add unsupported facts, or change the recommendation while simplifying it. If an error is identified, explicitly correct it rather than silently rewriting it.
- Prefer natural prose. Use a table or diagram when it reduces comprehension effort; no additional Skill call or artifact is required by default.
- Do not resume the original task, change code, introduce a new solution, or expand into research or review. Deliver the explanation directly without unnecessary background or an account of the rewriting process.
