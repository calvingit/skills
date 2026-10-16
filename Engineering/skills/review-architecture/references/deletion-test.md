# Deletion Test

The deletion test only answers whether a Module concentrates complexity behind its Interface. It does not judge whether the Module sits on the right boundary, owns the right state, or obeys the right dependency direction.

Imagine deleting the target Module:

- Complexity mostly vanishes; callers just call the downstream capability: `pass-through`.
- Callers only have to put back a little logic close to the original Interface: `shallow`.
- Hidden rules, ordering, error handling, or side effects spread back across several callers: `deep`.

Ask what callers would have to know again — not how many lines disappear. Record the basis: call order, invariants, error modes, retry, cache, or state coordination landing on which callers.

## Interpretation

- `pass-through` / `shallow`: the current Module shape may lack leverage. Worth an architecture-review candidate.
- `deep`: the Module is concentrating complexity. Do not split it just because the internals are large.
- `deep` is not an architecture free pass. Wrong ownership, boundary, lifecycle, or dependency direction still stands on its own evidence.

Pair with "the interface is the test surface": if production callers and tests both have to go *past* the Interface to verify load-bearing behaviour, the problem is likely the Interface or the boundary, not Implementation size.
