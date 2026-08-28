# Error Handling

Every Pi invocation must have a host-controlled, task-appropriate timeout and a captured exit status. Do not wait forever and do not silently replace missing output with success.

| Condition | Result | Retryable |
| --- | --- | --- |
| Pi executable missing | `blocked: pi_not_installed` | No |
| Requested model unavailable | `blocked: model_unavailable` | No |
| Authentication, quota, or permission failure | `failed: authentication_or_quota` | No |
| HTTP 429 or concurrent-request limit | `failed: rate_limited` | Yes |
| HTTP 500, 502, 503, or 504 | `failed: gateway_error` | Yes |
| Host timeout | `failed: timeout` | Yes |
| Empty stdout report | `failed: empty_report` | Only with new evidence |
| No JSONL session | `failed: session_not_persisted` | Only with new evidence |
| Multiple unknown JSONL sessions | `failed: ambiguous_session` | No |
| Write outside implementation ownership | `policy_violation` | No |
| Some committee members fail | `partial` | Per member |
| Preflight prerequisite fails before edits | `blocked` or `failed` | No unless new evidence |
| Pi requests work outside its slice | `ownership_request` | No; primary agent decides |

On timeout or cancellation, terminate the exact host execution session, then preserve any prompt, report fragment, and JSONL for inspection. Confirm the child Pi process is gone before returning control.

Do not automatically retry. If the primary agent explicitly retries a retryable failure:

- respect an authoritative retry-after value when present;
- use the exact original session when it exists;
- add new evidence or a narrower question;
- perform at most the explicitly authorized retry;
- never turn repeated failure into an implicit loop.

Return the category, model/member, exit status, whether a session was persisted, whether retry is reasonable, and the artifact directory. Do not expose credentials or full gateway responses containing sensitive values.

## Post-failure disposition

After any `blocked`, `failed`, `partial`, or `ownership_request` result:

1. Confirm the exact Pi process has exited.
2. Preserve the prompt, report fragment, JSONL session, heartbeat, and worktree diff.
3. Inspect actual status, complete diff, changed paths, and verification evidence.
4. Continue in the existing worktree only if the diff is small, in-scope, and directionally clear; otherwise switch to a clean linked worktree or let the primary agent implement it.

Do not treat `completed` as acceptance. `completed` means the Pi turn produced valid artifacts. `accepted` is a primary-agent decision after independent verification, simplification, and review.
