# ADR Format

Use only when the project has no existing ADR or decision-record format.

```markdown
# <Short decision title>

<Background, decision, and reason in one to three sentences.>
```

Record an ADR only when all three hold: changing the decision later is costly, a future maintainer would be surprised without the context, and there were real alternatives at the time. Add Status, Considered Options, and Consequences only when they add lasting value.

Directory and numbering follow the project's convention. With no convention, do not invent a fixed `docs/adr/`. Decide the write location first, then increment whatever numbering that directory already uses.
