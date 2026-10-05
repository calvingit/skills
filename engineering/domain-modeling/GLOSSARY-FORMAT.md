# Glossary Format

Use only when the project has no existing domain glossary format. This is a default shape, not a required filename or migration.

```markdown
# Glossary

<Optional: the business context whose vocabulary this glossary defines.>

## Language

**Order**
<One or two sentences: what it is.>
_Avoid_: Purchase, Transaction
```

Rules:

- When several words name the same concept, pick one canonical term; list the rest under `_Avoid_`.
- Definitions say what the thing *is*, in one or two sentences. Not what the code does.
- Record concepts unique to this project's domain. Not timeout, error type, or a generic design pattern.
- If there really are several contexts, a root `GLOSSARY-MAP.md` may point at each. Reuse an existing map/name when present. If ownership is unclear, ask. Don't guess.
- Create the file only after the first term is confirmed and the write location is clear. Don't pre-create an empty doc.
