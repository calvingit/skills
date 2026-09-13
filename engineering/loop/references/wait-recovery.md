# Waiting and recovery

Read when a role has not returned, a wait/command fails, or execution is interrupted. The timing policy and completion gates are defined in [Loop](../SKILL.md); use the actual runtime's message, status, and cancellation semantics, not an assumed universal API.

## Interpret available evidence

| Observation | Decision |
| --- | --- |
| One or several wait windows end while the role is running | Check available runtime state; use the one-time inquiry below if no new progress is available, then continue under the inactivity and any explicit total limits. Do not close or duplicate the role. |
| No report or file changes, including a read-only reviewer or simplifier | Progress is unknown; absence of a diff is not a stall or a no-change conclusion. |
| Status cannot be read, or local `ps` finds no process | Record the visibility limit, use available native queries/waits, and retain the recorded activity time and deadlines. |
| Runtime reports completion but no result has arrived | Retrieve the original report; a delayed notification is not role failure. |
| A command times out, fails, or lacks permission | Collect the command, exit status if available, partial output, and blocker; recover that check. This does not establish a code defect or global native-agent failure. |
| The inactivity threshold is reached | Verify current state and any running command using the procedure below before deciding to stop. |
| An explicit total execution budget expires | Begin orderly stopping and recovery; activity does not extend this limit or establish failed acceptance. |

Use source and recency together for the same execution: current explicit runtime facts take precedence over an Agent's self-report, and an old running observation cannot override a newer confirmed stop. File changes do not prove liveness. If the environment prevents further work, retain recoverable state and report the concrete limitation.

## Activity and threshold handling

Qualifying activity must belong to the same handle and attempt/snapshot: a new Agent progress message, command/stage result, runtime tool event or output, or a fresh reply to the inquiry. A reply proves responsiveness, not useful progress. Repeated `running` snapshots, replayed messages/reports, local heartbeat events, sending an inquiry, and unattributed file changes do not renew the threshold.

Record the evidence identity/source and its event time, using first observation time only for demonstrably new live activity without a source timestamp. Renew from the latest qualifying activity time, not from the time an old event is reread. On context recovery, reuse the stored times and inquiry record; if timing or freshness cannot be established, record the visibility gap rather than inventing a new 600-second window or claiming expiry. For example, activity at second 599 moves the default inactivity deadline to second 1199, but cannot move an explicit total deadline.

At the inactivity threshold:

1. Query available native state and retrieve any completed result. New activity renews the threshold; confirmed failure, cancellation, or an expired explicit total budget follows stopping/recovery below.
2. If a specific command is still running, check its actual status and applicable command timeout/waiting rules. A long tool call can delay Agent messages. Continue when those rules justify waiting, recording the command evidence and next native check; do not convert a generic `running` snapshot into activity or an indefinite exemption. The next check is an observation point, not a renewed activity deadline.
3. If there is still no new activity and no command evidence justifying further waiting, begin orderly stopping/recovery. Record inactivity or insufficient execution visibility as the reason, not a proven stall or failed acceptance. Acknowledging a cooperative stop request does not revoke that request; confirm its outcome before further work.

Use existing `.loop/` execution notes and native waits; do not add a heartbeat service, script polling, or another Agent state machine. Renewal never waives required verification/review or authorises overlapping work.

## One progress inquiry per execution

After a wait window ends, check available runtime state before deciding whether to inquire. Retrieve results for a completed execution. Handle explicit failure, confirmed stop, cancellation, or expired explicit total budget through the existing recovery rules; do not insert a ping first.

1. If the execution is unfinished and there is no new progress information, inquire once before the inactivity threshold or an explicit total deadline is reached. This includes a running role without new stage/command/results information and a role whose runtime state is unknown. If new progress is available, keep waiting; a later window may use the still-unused inquiry.
2. Read the existing `.loop/` execution notes before sending. Record the inquiry time and request against the original handle and attempt/snapshot, and any send result or visibility limit. Never send another soft ping for that execution after another wait, a return to unknown status, or context recovery. An uncertain send result is not grounds to repeat the inquiry.
3. Use only native messaging that supports input to a running Agent without interrupting it. If unavailable, record the limitation and continue normal waits under the recorded timing policy; it does not block verify or code-review. Do not substitute an interrupt or launch an external CLI.
4. Give the role a normal native wait/status cycle to respond subject to the inactivity threshold and any explicit total deadline. Record its reply, or that no reply has been received as of the observation time; attach a later reply to the same execution. Resume waiting unless actual evidence requires recovery. Replies may be delayed until the current tool call ends; absence of a reply is only missing extra information, not failure, stopped execution, or a reason to turn a known running state into unknown.

Use a short request with these meanings; no JSON envelope or fixed reply format is required:

> Please report your current stage, running command, completed results, and blockers. If still executing, do not stop work; just return current progress.

Sending the inquiry does not renew any deadline. A fresh reply renews inactivity as described above, but never extends an explicit total budget. Do not add a separate pong deadline. At the inactivity threshold, use state/command verification above; at explicit total expiry, proceed with orderly stopping. A stopping request for partial results is distinct from soft ping and is not prevented by the one-inquiry limit.

## Stop before takeover

1. Record the actual reason: observed error, confirmed blocker, inactivity after state verification, insufficient execution visibility, explicit total-budget expiry, or user cancellation. First recover a failed command or query when possible; one failed step does not automatically require terminating the role.
2. If cooperative stopping is supported, request partial results, the current step, and unfinished work, then give the role a response opportunity through native waiting/status checks. An unrecoverable error or urgent cancellation may use the runtime's immediate-stop semantics.
3. Use supported stop/interrupt/close operations and confirm a terminal or stopped state. Acknowledgement of a cancellation request alone does not confirm termination. If stopping is unconfirmed, preserve the blocker and do not start overlapping work.
4. For a writer, inspect and preserve its partial diff after confirmed stop. Check whether related commands are still running; do the same before taking over a verifier's commands in the shared environment. Never run overlapping writes or duplicate checks while their execution state is unknown.
5. Associate any late report with its original handle, attempt, and reviewed code version/snapshot. Accept it only if still applicable; never silently assign it to a replacement execution.
6. Resume the original role when possible, otherwise redispatch only the affected role with its current evidence and remaining work. Keep the ticket attempt when recovering verification/review; use a correction attempt only for an actual implementation defect. Main-agent substitution requires the explicit authority described in Loop. Do not endlessly redispatch an unchanged failure: retain the incomplete stage with the concrete blocker and release condition if recovery cannot progress.

Missing required reports keep ticket approval false or final delivery pending. Preserve completed tickets when finalization is interrupted. Keep partial reports and recovery notes in the existing task `.loop/` records; do not introduce a second attempt state machine or mislabel interrupted execution as failed product acceptance.
