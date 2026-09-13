# Waiting and recovery

Read when a role has not returned, a wait/command fails, or execution is interrupted. The execution budget and completion gates are defined in [Loop](../SKILL.md); use the actual runtime's message, status, and cancellation semantics, not an assumed universal API.

## Interpret available evidence

| Observation | Decision |
| --- | --- |
| One or several wait windows end while the role is running | Check available runtime state; use the one-time inquiry below if no new progress is available, then continue within the original budget. Do not close or duplicate the role. |
| No report or file changes, including a read-only reviewer or simplifier | Progress is unknown; absence of a diff is not a stall or a no-change conclusion. |
| Status cannot be read, or local `ps` finds no process | Record the visibility limit, use available native queries/waits, and retain the original deadline. |
| Runtime reports completion but no result has arrived | Retrieve the original report; a delayed notification is not role failure. |
| A command times out, fails, or lacks permission | Collect the command, exit status if available, partial output, and blocker; recover that check. This does not establish a code defect or global native-agent failure. |
| The recorded execution budget expires | Begin orderly stopping and recovery; do not infer failed acceptance or a passed review. |

Use source and recency together for the same execution: current explicit runtime facts take precedence over an Agent's self-report, and an old running observation cannot override a newer confirmed stop. File changes do not prove liveness. If the environment prevents further work, retain recoverable state and report the concrete limitation.

## One progress inquiry per execution

After a wait window ends, check available runtime state before deciding whether to inquire. Retrieve results for a completed execution. Handle explicit failure, confirmed stop, cancellation, or exhausted budget through the existing recovery rules; do not insert a ping first.

1. If the execution is unfinished and there is no new progress information, inquire once while budget remains. This includes a running role without new stage/command/results information and a role whose runtime state is unknown. If new progress is available, keep waiting; a later window may use the still-unused inquiry.
2. Read the existing `.loop/` execution notes before sending. Record the inquiry time and request against the original handle and attempt/snapshot, and any send result or visibility limit. Never send another soft ping for that execution after another wait, a return to unknown status, or context recovery. An uncertain send result is not grounds to repeat the inquiry.
3. Use only native messaging that supports input to a running Agent without interrupting it. If unavailable, record the limitation and continue normal waits and the original budget; it does not block verify or code-review. Do not substitute an interrupt or launch an external CLI.
4. Give the role a normal native wait/status cycle to respond within the remaining budget. Record its reply, or that no reply has been received as of the observation time; attach a later reply to the same execution. Resume waiting unless actual evidence requires recovery. Replies may be delayed until the current tool call ends; absence of a reply is only missing extra information, not failure, stopped execution, or a reason to turn a known running state into unknown.

Use a short request with these meanings; no JSON envelope or fixed reply format is required:

> Please report your current stage, running command, completed results, and blockers. If still executing, do not stop work; just return current progress.

The inquiry and response never reset or extend the 10-minute execution budget. Do not add a pong deadline or close after a response window expires. At budget expiry, proceed with orderly stopping; its request for partial results is distinct from soft ping and is not prevented by the one-inquiry limit. Keep these notes in existing execution records, without a heartbeat service, script polling, or another Agent state machine.

## Stop before takeover

1. Record the actual reason: observed error, confirmed blocker, elapsed budget, or user cancellation. First recover a failed command or query when possible; one failed step does not automatically require terminating the role.
2. If cooperative stopping is supported, request partial results, the current step, and unfinished work, then give the role a response opportunity through native waiting/status checks. An unrecoverable error or urgent cancellation may use the runtime's immediate-stop semantics.
3. Use supported stop/interrupt/close operations and confirm a terminal or stopped state. Acknowledgement of a cancellation request alone does not confirm termination. If stopping is unconfirmed, preserve the blocker and do not start overlapping work.
4. For a writer, inspect and preserve its partial diff after confirmed stop. Check whether related commands are still running; do the same before taking over a verifier's commands in the shared environment. Never run overlapping writes or duplicate checks while their execution state is unknown.
5. Associate any late report with its original handle, attempt, and reviewed code version/snapshot. Accept it only if still applicable; never silently assign it to a replacement execution.
6. Resume the original role when possible, otherwise redispatch only the affected role with its current evidence and remaining work. Keep the ticket attempt when recovering verification/review; use a correction attempt only for an actual implementation defect. Main-agent substitution requires the explicit authority described in Loop. Do not endlessly redispatch an unchanged failure: retain the incomplete stage with the concrete blocker and release condition if recovery cannot progress.

Missing required reports keep ticket approval false or final delivery pending. Preserve completed tickets when finalization is interrupted. Keep partial reports and recovery notes in the existing task `.loop/` records; do not introduce a second attempt state machine or mislabel interrupted execution as failed product acceptance.
