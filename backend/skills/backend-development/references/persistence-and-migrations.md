# Persistence and migrations

Read for schema changes, backfills or data repairs. The application's invariants
and deployment model determine what must remain compatible; database-specific
behaviour comes from the actual version and operational rules.

## Integrity and concurrency

Identify writes that must succeed or fail together, concurrent changes to the
same state, required read consistency, and effects on queries, indexes,
constraints and data volume. Put transactions around real atomicity boundaries,
not entire request flows by default.

Prefer database constraints for invariants it can enforce reliably. Keep
user-facing validation and domain errors at the appropriate application boundary.

## Schema compatibility

Account for existing data and application versions running during deployment.
Do not require every instance to switch at once unless deployment guarantees it.
Application rollback does not undo data changes: confirm that the old version can
read data written by the new version.

Remove an old field or read/write path only after evidence shows required callers,
jobs and supported rollback versions no longer depend on it. Check the database's
actual DDL, locking, replication and load rules; application compatibility checks
do not replace database-specific change review.

## Backfills and repairs

Use bounded batches and resumable progress while preserving concurrent business
writes. A checkpoint must not skip uncommitted work, and repeating a batch must
not corrupt or duplicate results. Verify affected records and remaining work,
not just the script's exit code.
