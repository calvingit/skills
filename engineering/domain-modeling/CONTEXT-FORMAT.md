# CONTEXT Format

Use only when the project has no existing domain-doc format.

```markdown
# <Context name>

<One or two sentences: what this context is, and why it exists.>

## Language

**Order**:
<One or two sentences: what it is.>
_Avoid_: Purchase, Transaction
```

Rules:

- When several words name the same concept, pick one canonical term; list the rest under `_Avoid_`.
- Definitions say what the thing *is*, in one or two sentences. Not what the code does.
- Record concepts unique to this project's domain. Not timeout, error type, or a generic design pattern.
- If there really are several contexts, a root `CONTEXT-MAP.md` may point at each. If ownership is unclear, ask. Don't guess.
- Create the file only after the first term is confirmed and the write location is clear. Don't pre-create an empty doc.
