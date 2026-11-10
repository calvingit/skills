---
name: find-docs
description: Fetch official documentation for a library or service at the relevant version.
---

# Documentation Lookup

Resolve the product, question, and relevant version from the user's request and available project manifests or lockfiles. Use current documentation when no project or requested version constrains the answer.

1. Prefer the project's official documentation, source, release notes, or versioned references. An index's ranking, reputation label, or retrieval time does not establish official ownership or freshness.
2. Use available documentation tools or browser/search access. When Context7 is appropriate, read [the CLI reference](references/context7.md), resolve the library ID, then query that ID:

   ```bash
   npx ctx7@latest library <name> "<query>"
   npx ctx7@latest docs <libraryId> "<query>"
   ```

   A valid ID supplied by the user can skip resolution. Keep queries free of secrets or proprietary source. A lookup does not authorise global installation, login, or changing sandbox/approval settings.
3. Match the requested version exactly when available. If it is unavailable, say so and look for official versioned sources; evidence from another version must be labelled, including any unverified applicability.
4. Answer the concrete question with source links and the applicable version. Distinguish documented behaviour from inference. Do not claim code examples were executed unless they were.
5. If an index fails or lacks coverage, use another accessible official source. Do not repeat the same failed request without new evidence, treat every network error as a sandbox problem, or substitute training knowledge for verified current docs. Report remaining evidence gaps.
