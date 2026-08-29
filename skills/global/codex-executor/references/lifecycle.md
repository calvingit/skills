# Codex Session Lifecycle

## States

```
created -> running -> completed
              |
              +-> interrupted -> resume
              |
              +-> failed
```

## Resume

Prefer continuing existing sessions for:
- interrupted execution
- missing tests
- incomplete implementation

```bash
echo "continue task" | codex exec resume --last
```

## Failure Classification

Environment failure:
- missing dependency
- permission issue

Task failure:
- incorrect assumption
- wrong implementation

Scope failure:
- unrelated refactoring
- excessive changes

Do not retry blindly.
