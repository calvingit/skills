---
name: verification-setup
description: Create or refresh project-local verification skills from repository evidence. Use when a project lacks a repeatable verification method, or its commands, surfaces, or evidence guidance have drifted.
---

# Verification Setup

Discover how this repository can establish observable behaviour, then create or refresh its project verification harness: the existing tools, execution recipes, and evidence guidance exposed through a local skill. Keep project-specific knowledge here; `verify` judges evidence against confirmed Acceptance Criteria (AC).

## Discover before designing

1. Read applicable instructions, Git status, project/domain docs, manifests, scripts, CI, test configuration, and relevant tests. Resolve the entry from the current task, then `verification_instructions` in the applicable Engineering Skills Profile, then repository conventions. A missing Profile or `auto` does not block discovery.
2. Identify relevant surfaces (UI, API, CLI, library, device), how to build/start them, how to drive them, what results and side effects can be observed, and how to isolate and clean up a run. Inspect versions, auth/seed needs, ports, devices and shared resources where applicable. Distinguish declared commands from checks actually executed.
3. Reuse existing harnesses and guides. Match each needed behaviour to a sufficient method; a framework name alone does not justify installing a tool. Separate behaviour, visual conformance and interaction quality. Ask only about unavailable facts or consequential choices that repository evidence cannot settle.

Scope setup to the requested surfaces. For a monorepo, include relevant shared dependencies and cross-surface journeys; do not assume one repository is one app. Reuse the domain glossary within its scope. Requirements define expected behaviour; source and tests reveal current capabilities, not new acceptance requirements.

## Create or refresh

Use the repository's local skill convention; default to `.agents/skills/verify-<surface>/`. Update an existing equivalent in place rather than creating a competing entry. Use one skill when the run/drive/isolation recipe is shared; split only when surfaces need distinct recipes. For multiple skills, reuse or create one concise navigation entry mapping surfaces and cross-surface journeys to their guidance, without duplicating commands.

Follow [the project harness contract](references/project-harness.md). Write concrete repository paths, commands or tool actions, prerequisites, observations and limits. Keep existing scripts as the execution authority; add a helper only when it removes repeated or fragile work. Do not add a generic runner, fixed test-level ladder, empty directories, or parallel configuration format.

Record a small feature map inline, or in referenced feature files when it improves navigation. For each covered feature, identify its requirement/doc source, entry point, drive method, expected observable result, side effects and unsupported scope. Distinguish confirmed expectations from unconfirmed coverage candidates. Reuse existing mappings; do not copy SPEC or turn the map into a new requirements authority. Mark mapped but unexercised paths explicitly.

Keep writes within local verification skills, necessary helpers and their navigation links. Do not repair product code or rewrite assertions, fixtures, snapshots or baselines to hide a failed run. When a missing tool or test capability requires dependency, CI or product changes, describe the smallest gap and handle it as separate implementation work under the caller's authority. Do not silently install a preferred framework.

Keep `verification_instructions` as the single Profile entry. Point it at the local skill or multi-surface index when this navigation change is authorised; preserve other fields and confirmed entries. Without a Profile, a short link in existing project instructions is enough; do not create a full Profile just for this skill. Respect scoped instructions and preserve unrelated edits.

## Prove the instructions

Follow the generated instructions from their documented starting state. Check prerequisites and instance identity, launch if needed, drive one representative feature through its public interface, capture the action and observable result, then clean up. Repeat for each distinct recipe created or changed. A library or short-lived CLI does not need a persistent server.

Use isolated test resources within the caller's permissions. Do not drive a user's shared session or mutate live business state. Clean up only resources this run owns, including after failure, and confirm evidence survives cleanup. Record actual commands/actions, working directory, versions/platform, revision plus relevant working-tree changes, exit codes and evidence paths in the caller's permitted output area. Keep current run logs out of stable Profile settings.

Report separately what was written and what ran. Successful smoke execution validates that recipe and exercised path only, not every mapped feature or product AC. If execution is blocked or fails, retain an explicitly labelled draft for the affected recipe, report the observation and release condition or required repair, and do not call it operational. A healthy command for another surface does not clear the gap.

## Maintain without widening scope

When guidance exists, compare it with the current sources and changed surfaces. Repair stale commands, paths, selectors, environment assumptions and mappings; remove obsolete guidance within scope, then rerun affected recipes. If nothing changed, verify the requested coverage without generating a cosmetic diff. Do not overwrite manual instructions or lower expected behaviour to match a regression. Return product failures and unresolved contract conflicts to their owner.

Report changed entries, reused tools, exercised coverage, retained evidence and outstanding gaps. Setup does not declare task acceptance, modify ticket state, or commit/push unless the caller authorised it.
