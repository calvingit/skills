# Report Rules

This reference owns report requirements for every audit mode. Mode-local finding formats and examples are optional aids and must not force extra sections, scoring, or effort estimates.

## Default response

Use the conversation language and concise Markdown in the conversation unless the user requested another output. State:

- Conclusion and the reviewed scope/baseline.
- Prioritised findings with evidence, trigger, impact, and minimal correction.
- Confirmed issues versus hypotheses and optional improvements.
- Inspected areas, meaningful exclusions, checks actually run, and remaining uncertainty. A multi-dimension audit includes a compact coverage table with confidence and evidence per selected dimension.

Do not ask for language or format when these defaults suffice. Do not create report or metadata files for conversation-only output. Reuse supplied decisions rather than reopening them.

## File output

Use the user's requested path and format; otherwise use the project's report convention with a task-specific filename. Never overwrite an unrelated report.

- `md`: save the same evidence-based report as Markdown.
- `html`: create a readable, self-contained report; inspect its rendered layout and links before delivery.
- `both`: keep Markdown and HTML findings and coverage consistent.
- `json`: follow `templates/audit-report.json`. Validate the result against the schema with an available JSON Schema validator. Report inability to validate instead of claiming a pass. Omit `scoreDashboard` when scores were not requested.

Read `templates/audit-report.md`, `templates/audit-report.html`, or `templates/issue-card.md` only when a detailed template report is requested. Reuse useful structure; remove irrelevant sections and unused score placeholders. Project and user format requirements take precedence. Do not copy example findings or invent scores to fill a template.

## Optional scoring and planning

Only when requested, use `rubrics/scoring.md` to report scores with evidence and coverage limits. Unassessed dimensions are excluded. No finding does not prove release readiness.

Give effort estimates, remediation plans, and historical metadata only when requested. Use a confirmed or established location for tracking, with no runtime-specific default directory.

## Validation

For all outputs, check actual evidence, selected-dimension coverage, matching counts, links, remaining placeholders, and redaction. An unavailable check must remain visible.

`scripts/report_lint.py` checks the legacy detailed Markdown/HTML template structure, not arbitrary reports or JSON. Run it only for reports intentionally using that full structure:

```bash
python3 <skill-dir>/scripts/report_lint.py --modes <selected-modes> <report-file>
```

For compact or customised reports, apply the semantic checks above; do not add irrelevant sections just to satisfy the legacy template linter. For JSON, use schema validation rather than this text linter.
