# When to Use Test Doubles

Prefer real, fast, deterministic dependencies, then existing project fakes, emulators or test adapters. Use a small test double where an external service, time, randomness, or a costly dependency prevents useful feedback.

Choose isolation based on the behaviour and risk under test. Mocking an internal collaborator is a warning when it copies the implementation's call graph or hides the behaviour being claimed; ownership alone does not determine whether a double is valid. State which boundary remains unverified and use a real integration check when that boundary matters to acceptance.

Use responses grounded in the dependency's contract, including relevant failures. A mock configured to return success cannot establish that the real integration works. Do not mock the target behaviour itself.

Reuse existing construction and dependency injection points. Add or change an interface only when real production callers or a concrete design need justify it; do not impose SDK wrappers, public setters or a new dependency-injection layer for testing alone.
