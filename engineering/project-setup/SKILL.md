---
name: project-setup
description: Detect and persist stable project engineering conventions in a separate Profile with an on-demand AGENTS.md link.
---

# Project Setup

Locate the project's established engineering sources and persist their stable entries in an Engineering Skills Profile. Default to `.agents/engineering-profile.md`; keep only its link and reading conditions in the applicable `AGENTS.md`. Setup is optional and does not gate ordinary engineering work.

## Discover

Read applicable instructions, Git status, README, existing task conventions, domain and architecture docs, requirement sources, verification guidance, and collaboration rules. Follow [Profile resolution](references/profile.md#resolve-and-load). Classify candidates as confirmed, inferred, missing, or conflicting; a directory or tool existing does not establish authority or operational capability.

Record only stable locations and policies. Do not store current requirements, task state, run results, commands, Agent/model choices, or Git permissions. Keep concrete verification recipes in existing guides or project-local skills. Do not create empty task, glossary, ADR, or harness scaffolding.

## Confirm and persist

1. Show the detection basis, proposed Profile, short `AGENTS.md` entry, and any existing configuration to migrate. Reuse confirmed values and existing paths; read [the Profile format and migration rules](references/profile.md) before writing.
2. Ask once for consequential choices that repository evidence cannot settle and confirmation of the proposed configuration. Choices already supplied by the caller count as confirmation. A custom conflicting value needs resolution; ordinary formatting or relocation already authorised by the caller does not require another approval.
3. Write or update the separate Profile and its link. Migrate a unique embedded Profile without losing confirmed or unknown fields, then remove the old block. Preserve unrelated instructions and edits. Never keep two active copies or silently choose between conflicting configurations.
4. Add project-specific engineering context in the Profile only where existing instructions do not already cover it. Use glossary terms within their domain; resolve material source conflicts before dependent work. Do not copy generic principles or invent architecture constraints.
5. Re-read changed files, check entries against actual sources and paths, confirm a unique Profile and intact unrelated instructions, and inspect the diff. Repeating setup with the same settings must not create duplicates or cosmetic changes.

## Verification ownership

Maintain `verification_instructions` as the navigation entry. Missing or `auto` means discover existing methods. A broken explicit entry is a configuration gap to report, not permission to silently replace it.

The Profile's Verification section summarises covered surfaces, method entries, prerequisites, and limits. Link to the authoritative recipe rather than copying its commands or feature map. Describe unexercised methods as declared capability, never as proven operational.

`verification-setup` owns creating, refreshing, and exercising project verification methods and updating this summary when authorised. `verify` independently chooses sufficient checks for the current acceptance criteria and judges evidence. Do not build the harness or declare task acceptance here.

## Report

Report changed entries, migration, confirmed values, items left to discovery, and unresolved conflicts or unverified capability. File existence does not establish that a Runtime loaded it or a recipe ran. Do not commit or push unless authorised.
