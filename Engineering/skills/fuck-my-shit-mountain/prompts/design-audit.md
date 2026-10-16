# Design Audit

Inspect contract clarity, dependency direction, side effects, responsibility placement, and design constraints confirmed by the project within the agreed project scope.

When available, use `review-architecture` and the design vocabulary of `codebase-design` for judgement. Do not start a redesign, interview, or implementation workflow. In a standalone installation, apply the local evidence and coverage rubrics; principles are investigation aids, not independent proof of a defect.

Trace representative callers, dependencies, and verification paths. Explain the actual behaviour or change scenario, affected responsibility, concrete consequence, and smallest correction. Check existing guards and accepted tradeoffs before reporting.

File length, parameter counts, style, and missing patterns are search cues only. Do not mandate abstraction, a new interface, or a rewrite without a demonstrated responsibility or maintenance problem. Missing evidence remains a limitation.

Report through `references/report-format.md`; keep coverage distinct from findings and merge duplicate causes across dimensions.
