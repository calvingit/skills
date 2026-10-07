---
name: verify-engineering
description: Verify changes to this skills repository's engineering instructions and state tools. Select static checks, graph/CLI regressions and isolated skill exercises according to the changed contract.
---

# Engineering repository verification

Run from the `skills` repository root. Requirements come from the confirmed task and applicable [repository instructions](../../../AGENTS.md); the capabilities below do not define new acceptance. This is a project-local method, not a globally installed engineering skill or an independent-verdict substitute.

## Choose evidence before implementation

Relate each current AC to a source, observation, sufficient method and prerequisites. State missing coverage. Combine methods when necessary; green formatting or protocol tests cannot establish the judgement of a Skill.

| Surface / source | Method and observation | Coverage limit |
| --- | --- | --- |
| Changed Skill metadata and references | Use the installed `skill-creator`'s `scripts/quick_validate.py` on each changed/new Skill directory. Parse changed `agents/openai.yaml` when present; resolve concrete local Markdown links from their containing file and inspect referenced anchors. Run `git diff --check`. | Valid syntax and references only; no proof of routing, contractual strength or Runtime loading. |
| Ticket graph, authority, transaction, CLI or delivery snapshot | `python3 engineering/shared/check.py`; inspect actual exit code and unittest output. Individual checks live in `engineering/shared/tests/`. Public commands and deployment requirements are documented in [the Loop guide](../../../docs/loop-runtime.md); inspect the [state-tool acceptance boundaries](references/state-tools.md) for protocol checks and Loop replay scenarios. | Graph/CLI/snapshot behaviour on temporary repositories. Does not execute a real Agent lifecycle or prove evidence truth. |
| Task contract, routing, source ownership, project harness or verification judgement | Exercise the changed Skills in an isolated fixture against confirmed requirements and actual public entry points; use the [behaviour scenarios](references/engineering-system-evaluation.md). Inspect decisions, created files, changed bytes, actual observations and limits. | Only exercised scenarios and their candidate/context. An expected answer, document review or a fake provider does not prove live provider/device/UI integration. |

The existing repository check entry for engineering state tools remains `python3 engineering/shared/check.py`. Changes to those tools require its suite; instruction changes require relevant metadata/link checks and semantic exercises proportional to risk. Do not treat all three rows as a compulsory pipeline for every edit.

For backend Skill changes, select relevant [backend behaviour scenarios and dated evaluations](references/backend-skills-evaluation.md). Historical text trials are not live database tests or proof of current effectiveness.

For session-level feedback research, use the [Retro evaluation protocol](references/retro-evaluation.md) with real session evidence. It is an optional experiment and owner-routing method, not a new delivery gate or formal retro Skill.

For the fixed-versus-risk-based close-out role comparison, use the [close-out role experiment](references/closeout-role-experiment.md). It defines the comparison protocol and decision conditions only; quick-implement and Loop close-out requirements are unchanged until reviewed evidence supports a change.

## Prepare, run and retain

- Record the candidate `HEAD` plus staged, unstaged and untracked task changes and excluded existing edits. Recheck affected evidence after changes; `HEAD` alone does not identify an uncommitted candidate.
- State-tool tests require Python 3.10+ and Git on macOS/Linux. Skill metadata validation additionally requires the installed `skill-creator` validator and its PyYAML dependency; resolve that installed location rather than recording a user's home path. Report unavailable prerequisites instead of installing them silently or claiming that gate ran.
- Use a caller-permitted temporary directory for behavioural fixtures and outputs. Give evaluation workers only the selected request, candidate Skill/reference paths and raw fixture inputs. Use independent contexts when judging acceptance; implementation self-checks remain local evidence.
- Drive the documented public CLI or library entry. For recipe setup, run the generated instructions from their starting state, capture a representative path for each distinct changed recipe, clean up owned resources and confirm retained evidence remains readable. A deliberately isolated fixture may omit servers, accounts or devices it does not need.
- Preserve actual commands/actions, working directories, Python/Git versions where relevant, exit codes, key output, candidate, executor, source references, fixture changes and evidence paths in the caller's receipt or permitted evidence directory outside product snapshots. Do not retain credentials. Keep run history out of this method and the Profile.
- After failure as well as success, stop only owned resources and remove owned temporary state. Keep requested proof artifacts until review is complete; report cleanup failures. Tests may create Python bytecode caches, which are ignored by this repository.

Return observations and uncovered scope to the caller. Global `verify` owns per-AC verdicts; the execution owner decides completion. Permission, external effects and Git publication still follow the current user authorization.
