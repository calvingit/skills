# Model Selection Policy

## Principles

Model selection is a runtime strategy, not part of the Codex executor contract.

The executor should optimize:

1. Task success rate
2. Cost efficiency
3. Latency
4. Reliability

Do not always select the strongest model.

This skill targets OpenAI Codex workflows. The default model profiles use the gpt-5.6 series.

---

# Default Model Profiles

## fast

Default model:

```
gpt-5.6-luna
```

Reasoning:

- low
- medium when needed

Use for:

- simple code lookup
- documentation changes
- formatting
- small deterministic edits
- simple test generation

---

## balanced

Default profile.

Default model:

```
gpt-5.6-terra
```

Reasoning:

- medium

Use for:

- feature implementation
- bug fixes
- normal refactoring
- test writing
- code review

This should be the starting point for most engineering tasks.

---

## deep

Default model:

```
gpt-5.6-sol
```

Reasoning:

- high
- xhigh only when justified

Use for:

- architecture changes
- complex debugging
- large migrations
- concurrency issues
- unfamiliar codebases
- repeated failed attempts

---

# Reasoning Selection

Start with the lowest sufficient reasoning level.

Increase reasoning when:

- root cause is unclear
- previous implementation failed
- multiple components interact
- correctness risk is high

Do not increase reasoning only because a task is large. Better context and verification are often more valuable.

---

# Model Escalation

Recommended escalation:

```
gpt-5.6-terra + medium
          |
          | blocked
          v
gpt-5.6-sol + high
          |
          | still blocked
          v
human review or additional investigation
```

Use gpt-5.6-luna only when the task is clearly simple and deterministic.

Do not blindly retry with a stronger model without improving context.

---

# Custom Model Mapping

Different environments may use custom model aliases or gateways.

Map equivalent capabilities when necessary:

```yaml
fast: <fast coding model>
balanced: <default coding model>
deep: <reasoning coding model>
```

The skill depends on capability profiles, not model aliases.
