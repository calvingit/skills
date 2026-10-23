---
name: verification-setup
description: Discover and record a project's verification capabilities, or create or refresh project-local verification skills from repository evidence. Use when a project lacks a repeatable verification method, its commands, surfaces, or evidence guidance have drifted, or only an inventory of existing methods is requested.
---

# Verification Setup

Discover how this repository can establish observable behaviour, then create or refresh its project verification harness: the existing tools, execution recipes, and evidence guidance exposed through a local skill. Keep project-specific knowledge here; `verify` judges evidence against confirmed Acceptance Criteria (AC).

Choose the scope from the request:

- **Discover only**: inventory existing methods and report them without modifying project files. The report lists each method's source, actual command, prerequisites, evidence scope, limits and execution status (not run). Update an existing Verification summary only when the caller explicitly authorises it, and keep it to navigation: surface, method entry, essential prerequisites, capability summary and limits, never a copied command list. Stop after [Discover before designing](#discover-before-designing). Do not create a local skill, feature map or helper, and do not run checks.
- **Create or refresh**: complete discovery, then read and follow [the project harness contract](references/project-harness.md), including authoring, registration, trial run and maintenance. Discovery alone never makes a method operational.

See [usage examples and design source](references/usage.md) when establishing an entry or planning an incremental refresh.

## Discover before designing

1. Read applicable instructions, Git status, project/domain docs, manifests, scripts, CI, test configuration, and relevant tests. Resolve the entry from the current task, then `verification_instructions` via [Profile resolution](../project-setup/references/profile.md#resolve-and-load), then repository conventions. A missing Profile or `auto` does not block discovery.
2. Identify relevant surfaces (UI, API, CLI, library, device), how to build/start them, how to drive them, what results and side effects can be observed, and how to isolate and clean up a run. Inspect versions, auth/seed needs, ports, devices and shared resources where applicable. Distinguish declared commands from checks actually executed.
3. For each method, report its source (script, config or manual guide), command, prerequisites, what the actual configuration and tests can show, and their limits. Derive the scope from the configured paths and assertions, not from the tool name, and do not rate confidence. Cite existing execution evidence only when it exists.
4. Reuse existing harnesses and guides. Match each needed behaviour to a sufficient method; a framework name alone does not justify installing a tool. Separate behaviour, visual conformance and interaction quality. Ask only about unavailable facts or consequential choices that repository evidence cannot settle.

Scope setup to the requested surfaces. For a monorepo, include relevant shared dependencies and cross-surface journeys; do not assume one repository is one app. Reuse the domain glossary within its scope. Requirements define expected behaviour; source and tests reveal current capabilities, not new acceptance requirements.

When setup is requested for a delivery, read its [Task Contract](../shared/task-contract.md) and relate current AC/source references to sufficient methods before implementation. Keep missing observations and unavailable prerequisites visible. This task mapping is a derived handoff, not stable Profile content or permission to redefine acceptance; broad project setup without a current task needs no invented AC.

## Create or refresh

Read and follow [authoring and registration](references/project-harness.md#author-and-register) before writing. Reuse existing methods and scripts; create only the requested local recipes, necessary helpers and navigation. The reference owns recipe layout, feature mapping and Profile updates.

Keep writes within local verification skills, necessary helpers and their navigation links. Do not repair product code or rewrite assertions, fixtures, snapshots or baselines to hide a failed run. When a missing tool or test capability requires dependency, CI or product changes, describe the smallest gap and handle it as separate implementation work under the caller's authority. Do not silently install a preferred framework.

## Prove the instructions

Run the [trial and cleanup protocol](references/project-harness.md#trial-run-and-maintenance) for each distinct recipe created or changed. Use only permitted isolated resources; never drive a user's shared session or mutate live business state. A blocked or failed recipe remains a labelled draft. A smoke pass proves only the exercised path, not the feature map or task AC.

## Maintain without widening scope

Refresh only affected guidance under the same [maintenance protocol](references/project-harness.md#trial-run-and-maintenance). Preserve manual instructions, unrelated edits and expected behaviour; return product failures and contract conflicts to their owner.

Report changed entries, reused tools, exercised coverage, retained evidence and outstanding gaps. Setup does not declare task acceptance, modify ticket state, or commit/push unless the caller authorised it.
