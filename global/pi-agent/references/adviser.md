# Adviser

Use one independent read-only Pi session for an outside opinion. The primary agent keeps ownership of analysis and the final decision.

1. Complete the primary agent's initial investigation and privately retain its findings.
2. Build a dossier containing the user request, relevant SPEC/PLAN or diff, constraints, source locations, and objective verification evidence. Do not include the primary agent's findings or preferred answer in the first Pi prompt.
3. Follow [session-protocol.md](session-protocol.md) with one member and the read-only tool list.
4. Require Pi findings to include an ID, impact, concrete file/symbol evidence, a reachable path, and missing verification.
5. Independently test each Pi claim against the repository and actual evidence.
6. Classify the result as `agreed`, `main-only`, `pi-only`, or `unresolved`.
7. For a material disagreement, write the primary agent's evidence and exact question to the next round and resume the original JSONL session.

Do not accept a finding because Pi sounds confident. Do not reject it because it conflicts with the primary agent. Evidence decides.
