# Operation outcomes and retries

Read when a write crosses a network or process boundary and retries, lost
responses, or partial completion can repeat a meaningful side effect. Establish
the actual provider and application contract before choosing a mechanism.

## Recover the outcome

- Confirmed success requires evidence of the intended effect. An accepted job
  response may only establish that work was queued.
- Confirmed failure requires evidence about whether any effect occurred. A
  compound operation may have completed only some steps.
- A timeout, disconnected caller, or lost response can leave the outcome unknown.
  Do not record definitive failure or issue a fresh operation solely for that
  reason.

Find the existing way to resolve uncertainty: operation-status lookup, a durable
result, a correlated callback, or an authorized reconciliation process. If none
exists, keep uncertainty explicit and identify the recovery decision needed.
Do not manufacture a success response or automatically compensate an effect
whose existence is unknown.

## Identify one business operation

Where idempotency is needed, determine:

- Who creates the operation identity, and whether retries preserve it. Identical
  payloads can represent separate intentional operations.
- Its scope, including caller or tenant, and what happens when the same identity
  is reused with different parameters.
- How concurrent duplicates are serialized or rejected. A check followed by an
  unprotected write is not sufficient.
- How the effect and its recorded outcome survive a crash between them. A local
  database transaction does not atomically commit a remote provider's effect.
- How long the provider or local store remembers the identity, and what happens
  to a delayed retry after that window.

Reuse the existing provider contract or persistence boundary. Do not prescribe
an idempotency table, distributed lock, or outbox without a concrete gap.

## Bound retries and recovery

Retry only if repetition is safe and the failure is plausibly transient. Check
SDK, client, worker, and caller policies together so nested retries do not
multiply attempts unnoticed. Keep attempts within the operation's time and
capacity budget; follow provider backoff and throttling semantics.

Cancellation or an expired caller deadline does not prove that the remote work
stopped. Separate stopping local retries from recovering an already-started
operation. Compensation is another business operation with its own failure and
duplicate semantics, not a database rollback.

Verify the relevant failure window: for example, effect committed but response
lost, two concurrent duplicates, or restart before the outcome was recorded.
Observe both the business effect and the caller-visible result using an isolated
fixture or existing safe test environment; do not cause real external effects
just to validate the policy.

Background: [AWS Builders' Library — Making retries safe with idempotent APIs](https://d1.awsstatic.com/builderslibrary/pdfs/making-retries-safe-with-idempotent-apis-malcolm-featonby.pdf).
The project's actual provider contract remains the authority for its semantics.
