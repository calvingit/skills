---
name: why
description: Use only when manually invoked by the user to investigate why a current design, constraint, or workaround exists using available historical evidence. Keep confirmed facts, supported inferences, hypotheses, and unknowns distinct.
---

# Why

Explain the historical rationale of a current design without treating its shape
as proof of its intent. Investigate the evidence available in the current
environment; do not assume a particular Git host, connector, CLI, transcript,
or model.

## Investigate

1. Anchor the question in the current system: relevant path or symbol, current
   behaviour, and the specific choice, limit, compatibility rule, or workaround
   to explain.
2. Search progressively, stopping when the evidence supports an answer:
   current code and tests; Git history; PRs, issues, ADRs, architecture docs, or
   changelogs; then available shared records such as chat, observability, error
   tracking, or analytics when they can answer the remaining question.
3. Establish the lineage: what changed, when it changed, the constraint or
   incident it addressed, and whether that evidence still explains the current
   behaviour.
4. Distinguish confirmed observations from supported inferences, competing
   hypotheses, and unknowns. A missing source is a coverage limitation, not
   permission to invent intent.

Do not search every possible source by default. Do not treat a commit message,
current test, or present-day convention as a complete explanation without
supporting evidence. Stop when additional history would not materially change
the conclusion.

## Output

Answer directly, then make the basis legible. Use headings only when helpful,
but keep these categories distinct:

- confirmed evidence;
- supported inference;
- competing hypothesis, when one materially remains;
- unknowns or evidence gaps.

Do not recommend a redesign unless the user asks for one. Historical rationale
can explain a design; it does not prove that the design remains appropriate.
