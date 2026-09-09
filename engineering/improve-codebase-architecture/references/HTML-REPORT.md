# HTML Report

Write the report to the OS temp directory as `architecture-review-<UTC timestamp>.html`. Style with inline CSS. Use Mermaid via CDN only when a graph relationship actually needs it. The report is one HTML file that opens in a browser. Nothing lands in the repo.

Each candidate card names the modules involved, the current friction, the proposed deepening, leverage and locality payoff, how tests would improve, a before / after visual, and recommendation strength. End with a Top recommendation explaining why it should enter `grilling` first.

Do not design the final Interface at candidate-report time. File count, directory taste, or personal aesthetics are not architecture problems. Keep a candidate that contradicts an ADR only when the friction is real enough to reopen that decision, and mark the conflict clearly.
