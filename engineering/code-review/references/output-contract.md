# Review Report

Return readable Markdown in the user's language. Lead with the conclusion: no required fixes found, fixes needed, or insufficient evidence. Wording and headings are flexible; this is a report for people, not a parsing protocol.

Include only the sections useful for this review:

- Scope, baseline, requirement source, and material exclusions.
- Actionable findings ordered by impact. Each needs a location, reachable trigger, consequence, proportionate correction, and how to verify it. Severity labels may help prioritisation.
- Optional follow-up, clearly separated from required fixes.
- Conflicting requirements, missing evidence, and what would resolve them.
- Evidence actually inspected or executed, including failed checks and their sources.

Merge duplicate symptoms. Omit empty sections and generic checklists. No findings does not prove completeness: make limitations explicit, especially when requirements or required verification could not be assessed. Do not hide a failed check behind a positive conclusion.

A caller can retain this report as a string and decide what to do next. Do not return a JSON envelope, duplicate machine fields, or special output for an orchestrator.
