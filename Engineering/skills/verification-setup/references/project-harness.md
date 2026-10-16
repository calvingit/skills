# Project harness contract

Use these responsibilities to write the local skill, not as a required CLI or schema. Omit inapplicable machinery and state meaningful limits. Another agent should be able to use the instructions without the setup conversation.

## Entry and selection

- Give `SKILL.md` valid `name` and `description` frontmatter naming the surface and invocation context.
- Identify covered surfaces, repository-relative working directories and authoritative requirement/domain sources. Map cross-surface journeys to all relevant entries.
- Describe available checks by what they prove, prerequisites and relative cost. Include focused selection where supported, plus mandatory project gates. Choose the least costly sufficient evidence; a quick check cannot substitute for an uncovered behaviour or required gate.
- State unsupported platforms, features and evidence types. Existing configuration is declared capability until exercised; a smoke run covers only its recorded path and environment.

For a current delivery, map each confirmed AC/source reference to the public observation, selected method, prerequisites, required evidence and remaining gap before implementation. Use a session note or existing task record; the reusable feature map below locates capabilities, not task completion. A method can support several criteria, but a gate or smoke check must not silently stand in for uncovered criteria.

## Capability freshness

Distinguish a documented method, a method exercised on a recorded path/environment, and evidence accepted for a current candidate. These are different claims, not a new persisted status schema. Link run receipts rather than putting PASS/FAIL history in the Profile.

Recheck relevant methods after changes to public entry points, commands, dependencies, fixtures, permissions, platform or isolation/cleanup assumptions. Refresh only affected recipes and navigation; unaffected methods remain usable. A stale configured entry is a reported gap even if discovery finds another method. Task evidence is reassessed by its consumer after candidate or environment changes; setup does not certify it.

## Prepare and doctor

Give exact setup/start actions, supported versions, required environment-variable names (never secret values), test data/auth preparation, readiness conditions, and a bounded readiness wait with a diagnostic on failure. Prefer existing project commands and tools. Explain how to confirm the right instance/build, resource ownership, and prerequisites before driving it. Do not use a healthy unrelated process as readiness evidence.

Identify isolation needs: unique ports, test databases, data directories, accounts, browser profiles or devices as applicable. If resources cannot be safely shared, require exclusive use rather than concurrent driving. Document which test-state mutations are allowed and where artifacts may be written. Do not claim a dry-run has no side effects without checking its actual behaviour.

## Drive and observe

Use real repository commands, selectors, routes or public library callers. Record preconditions, actions, expected results and observable side effects. Prefer stable semantic handles over coordinates. Exercise the relevant public boundary; internal setters and test-only shortcuts cannot prove a path they bypass.

Name mocked boundaries and the limits they impose. A simulated external response cannot prove a real provider integration. Behavioural tests alone do not prove visual or UX acceptance; specify comparison with an agreed visual reference or human assessment when required, without claiming a screenshot proves interaction timing.

## Evidence and cleanup

Specify where the run stores action/result evidence, actual commands or tool calls, exit codes, environment, and the tested revision including relevant uncommitted changes. Existing project report formats suffice. Preserve only necessary data and omit credentials or personal data from retained output.

Capture results before teardown. Stop only owned processes and remove only owned temporary state; never kill by process name or reset shared data. Run cleanup after unsuccessful attempts too. Retain proof artifacts and confirm they remain readable afterward. Report cleanup failures and remaining resources rather than claiming the environment is clean.

## Minimal feature entry

Use an inline table for a small harness; split files only when useful:

| Feature / source | Preconditions and public entry | Drive / check | Expected result and side effects | Coverage limits |
| --- | --- | --- | --- | --- |

Populate with repository facts and confirmed expectations; omit this empty skeleton from the generated output. Include alternative entries or failure paths only when they are relevant to the requested coverage. Link to existing tests/docs instead of copying them. Keep smoke-run coverage distinct from the full map.
