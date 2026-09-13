# Waiting and recovery

Read when a role has not returned, a wait/command fails, or execution is interrupted. The execution budget and completion gates are defined in [Loop](../SKILL.md); use the actual runtime's message, status, and cancellation semantics, not an assumed universal API.

## Interpret available evidence

| Observation | Decision |
| --- | --- |
| One or several wait windows end while the role is running | Continue waiting within the original budget; do not close or duplicate the role. |
| No report or file changes, including a read-only reviewer or simplifier | Progress is unknown; absence of a diff is not a stall or a no-change conclusion. |
| Status cannot be read, or local `ps` finds no process | Record the visibility limit, use available native queries/waits, and retain the original deadline. |
| Runtime reports completion but no result has arrived | Retrieve the original report; a delayed notification is not role failure. |
| A command times out, fails, or lacks permission | Collect the command, exit status if available, partial output, and blocker; recover that check. This does not establish a code defect or global native-agent failure. |
| The recorded execution budget expires | Begin orderly stopping and recovery; do not infer failed acceptance or a passed review. |

Progress requests ask for the current stage, running command, completed results, and blockers. Allow a native wait/status cycle for a response; do not repeatedly demand immediate wrap-up. Keep queries consistent with runtime message semantics, without adding a heartbeat protocol. If the environment prevents further work, retain recoverable state and report the concrete limitation.

## Stop before takeover

1. Record the actual reason: observed error, confirmed blocker, elapsed budget, or user cancellation. First recover a failed command or query when possible; one failed step does not automatically require terminating the role.
2. If cooperative stopping is supported, request partial results, the current step, and unfinished work, then give the role a response opportunity through native waiting/status checks. An unrecoverable error or urgent cancellation may use the runtime's immediate-stop semantics.
3. Use supported stop/interrupt/close operations and confirm a terminal or stopped state. Acknowledgement of a cancellation request alone does not confirm termination. If stopping is unconfirmed, preserve the blocker and do not start overlapping work.
4. For a writer, inspect and preserve its partial diff after confirmed stop. Check whether related commands are still running; do the same before taking over a verifier's commands in the shared environment. Never run overlapping writes or duplicate checks while their execution state is unknown.
5. Associate any late report with its original handle, attempt, and reviewed code version/snapshot. Accept it only if still applicable; never silently assign it to a replacement execution.
6. Resume the original role when possible, otherwise redispatch only the affected role with its current evidence and remaining work. Keep the ticket attempt when recovering verification/review; use a correction attempt only for an actual implementation defect. Main-agent substitution requires the explicit authority described in Loop. Do not endlessly redispatch an unchanged failure: retain the incomplete stage with the concrete blocker and release condition if recovery cannot progress.

Missing required reports keep ticket approval false or final delivery pending. Preserve completed tickets when finalization is interrupted. Keep partial reports and recovery notes in the existing task `.loop/` records; do not introduce a second attempt state machine or mislabel interrupted execution as failed product acceptance.
