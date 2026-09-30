# Review Report

Return readable Markdown in the user's language. Lead with the conclusion: no required fixes found, fixes needed, or insufficient evidence. Wording and headings are flexible; this is a report for people, not a parsing protocol.

Include only the sections useful for this review:

- Scope, baseline, requirement source, and material exclusions.
- Actionable findings ordered by impact. Each needs a location, reachable trigger, consequence, evidence, proportionate correction, and how to verify it. State whether it requires a fix in the current change; severity alone does not decide that.
- Optional follow-up, clearly separated from required fixes.
- Conflicting requirements, missing evidence, and what would resolve them.
- Evidence actually inspected or executed, including failed checks and their sources.

Merge duplicate symptoms. Omit empty sections and generic checklists. No findings does not prove completeness: make limitations explicit, especially when requirements or required verification could not be assessed. Do not hide a failed check behind a positive conclusion.

Do not return a JSON envelope or duplicate machine fields.
