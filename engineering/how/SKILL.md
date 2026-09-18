---
name: how
description: Use only when manually invoked by the user to explain how current code works by tracing relevant production paths. Do not investigate historical rationale, diagnose a fault, or recommend a target design.
---

# How

Build a useful mental model of the current implementation. Answer what happens
now, where it happens, who owns each responsibility, and what callers need to
know. Do not turn an explanation into a design review or a line-by-line tour.

## Investigate

1. State the target behaviour, module, or flow. Keep the scope to the question
   and its necessary direct dependencies.
2. Locate the relevant entry point, composition or configuration boundary, and
   a representative production path. For a small function or module, explain it
   directly.
3. Trace only far enough to show the important data and control flow, owners,
   external boundaries, error or lifecycle behaviour, and invariants.
4. Read related tests when they show how the behaviour is observed. Treat tests
   as evidence of coverage, not automatic proof of all runtime behaviour.
5. Separate facts observed in code or runtime evidence from reasonable
   inferences and unverified paths. Stop once the question is answered.

Explain the smallest coherent model that helps the reader navigate or change the
system. Use a flow, a short example, or an ownership map when it clarifies the
answer. Do not inspect the whole repository merely to make the explanation feel
complete.

## Output

Adapt the response to the question. Useful sections can include an overview,
the representative flow, where responsibilities live, and important invariants
or gotchas. Preserve uncertainty instead of filling gaps from convention.
