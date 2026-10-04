# Testing Audit Prompt

Use the fuck-my-shit-mountain skill in **testing mode**.

Shared setup, coverage, report template, HTML, and lint rules live in `references/report-format.md`; load that reference before producing the report.

Focus on whether the tests provide real confidence in the codebase.

For assertion credibility, over-mocking, implementation coupling and test-only
production paths, read [testing authenticity](testing-authenticity-audit.md).
This prompt owns coverage, test levels and infrastructure.

For a coverage gap, identify the behaviour, smallest useful test case, failure it would catch and sufficient test level. Prioritise by actual risk; a gap does not by itself establish that release must be blocked.

## Audit Areas (see principles 8.1–8.5)

### Coverage Quality (not quantity)
- Critical paths without test coverage
- Error handling paths without test coverage
- Edge cases in input validation
- Boundary conditions
- Failure mode testing

### Test Types
- Unit test coverage of core logic
- Integration test coverage of external interfaces
- End-to-end test coverage of critical user flows
- Snapshot / golden file test quality
- Property-based or fuzz test coverage where appropriate

### Missing Tests
- Regression tests for past bugs
- Concurrency / race condition tests
- Performance / benchmark tests
- Upgrade / migration tests
- Configuration permutation tests
- Security tests (auth bypass, injection, permission)

### Test Infrastructure
- CI test execution (speed, parallelism, ordering)
- Test data management (fixtures, factories, cleanup)
- Test isolation (shared state between tests)
- Test environment consistency
- Test reporting (what breaks, where, why)

## Attitude

1. **Be exhaustively systematic.** Check in-scope critical paths, error paths, edge cases, and test layers. Follow the skill's coverage strategy and document exclusions honestly.
2. **Do not be a yes-man.** Report testing gaps even if the user says "we have good coverage." Coverage percentage does not equal confidence.
