# Coverage Confidence Rubric

Coverage confidence describes how completely a selected audit dimension was inspected. It is separate from finding confidence: a single finding can have High confidence even when the dimension's overall coverage is Medium.

## Levels

### High

- A file inventory was built with project-aware search.
- Entry points, critical flows, boundary files, configs, tests, and release/dependency artifacts relevant to the selected dimension were inspected.
- Important generated/vendor/build paths were intentionally excluded and documented.
- Relevant static checks, test commands, or targeted searches were run when practical.
- No important area for the selected dimension was skipped.

### Medium

- Main flows and representative files were inspected.
- Some secondary paths, environment-specific configs, generated artifacts, or runtime-only behavior could not be fully checked.
- The audit still has enough evidence to identify likely systemic risks.
- Any zero-finding conclusion is limited to the inspected scope.

### Low

- The audit relied on sampling, metadata, naming, or narrow searches.
- Critical runtime behavior, deployment config, data stores, or external interfaces could not be inspected.
- Findings may still be valid, but absence of findings is weak evidence.
- Scores should be conservative and must explain the coverage limit.

### Not Assessed

- The dimension is outside the selected mode, not applicable to the project, or inaccessible.
- Do not score the dimension.
- If the report template needs the row, mark it as "not assessed" and explain why.

## Reporting Coverage

`references/report-format.md` owns presentation requirements. For multi-dimension reports, use a compact coverage matrix:

| Dimension | Coverage | Evidence inspected | Exclusions / limits |
|-----------|----------|--------------------|---------------------|

For a single dimension, the same information can be concise prose; do not create a separate section or repeat the matrix merely to satisfy this rubric:

- Coverage: High / Medium / Low / Not assessed
- Inspected evidence: files, commands, patterns, or runtime surfaces checked
- Exclusions / limits: what was not checked and why

## Scoring Interaction

Apply these rules only when scores were requested:

- A dimension with zero findings can receive 10.0 only when coverage is High.
- Medium coverage can still support a good score, but the justification must mention the limit.
- Low coverage should not produce a high-confidence "clean" conclusion.
- Not assessed dimensions are excluded from the overall score.
- Do not use coverage confidence to downplay confirmed findings. It only qualifies completeness.
