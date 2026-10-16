# Lifecycle and resource limits

Read when changing workers, long-running requests, cancellation, shutdown, or
capacity behavior. Inspect the framework, deployment configuration, and relevant
queue/client settings; do not assume a signal or a cancelled future stops work.

## Ownership during shutdown and cancellation

Trace when the process stops admitting new requests or claiming work, how it
drains work already accepted, and what happens when its shutdown deadline expires.
Match this to the actual deployment termination window.

For a worker, identify when completion is acknowledged relative to durable side
effects. Determine who can reclaim unfinished work after a crash or lease expiry,
and whether the original worker can still write after another worker takes over.
Preserve the infrastructure's actual delivery guarantees; acknowledging early or
assuming exclusive ownership can lose or duplicate effects.

For cancellation, distinguish stopping the caller's wait from stopping execution.
Propagate cancellation through supported boundaries where the contract requires
it, release owned resources, and account for work that cannot be cancelled.
Detached work needs an existing owner and a way to observe its result. Do not
introduce a background task merely to hide timeout or shutdown failures.

## Bound admitted work

For each affected scarce resource, find the configured concurrency, queue or
batch bound, and the behavior at capacity. Include database connections, worker
slots, downstream calls, buffered payloads, and retry traffic only as relevant.

- A concurrency limit with an unbounded waiting queue can still exhaust memory
  or make deadlines meaningless.
- Increasing workers can move saturation to the database or downstream service.
- Retrying overload can increase the load that caused it. Consider total attempt
  volume across layers, not just one client's retry count.
- Decide where admission waits, rejects, or applies backpressure using the
  existing service contract. Do not silently drop accepted work.

Choose limits from existing budgets and observed workload, not universal values.
Reuse current infrastructure before proposing a new queue, limiter, or circuit
breaker. Record an unresolved capacity assumption when measurements are absent.

## Evidence

Use the smallest isolated check for the changed boundary: shutdown with work in
flight, cancellation during a dependency call, interruption before acknowledgement,
or saturation of the affected pool. Observe whether work was completed, reclaimed,
rejected, or left unresolved, and whether resources were released. Process exit
or a successful HTTP response alone does not prove the lifecycle contract.

Background: [Google SRE — Handling Overload](https://sre.google/sre-book/handling-overload/).
