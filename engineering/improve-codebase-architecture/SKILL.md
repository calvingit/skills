---
name: improve-codebase-architecture
description: Scan a codebase for deepening opportunities, present them as a visual HTML report, then grill through whichever one you pick.
---

# Improve Codebase Architecture

This is the **active-candidate mode** of `review-architecture`, not a separate flow. Load it when architecture review should hunt for deepening opportunities on shallow modules. Ordinary architecture review does not load this file.

Surface architectural friction and propose **deepening opportunities** — refactors that turn shallow modules into deep ones. Use the `codebase-design` vocabulary exactly: **module**, **interface**, **depth**, **seam**, **adapter**, **leverage**, **locality**. Don't drift into "component," "service," "API," or "boundary."

## Process

1. **Scope before you scan.** If the user named a module, subsystem, or pain point, take it. Otherwise walk a stretch of git history for hot spots — files and areas that keep coming up. Read the project's glossary, related ADRs, and `codebase-design` first.

2. **Find candidates.** Explore organically. Don't manufacture candidates from a fixed checklist. Look for:
   - Understanding one concept requires bouncing between many small modules.
   - Modules are **shallow** — interface nearly as complex as the implementation.
   - Tests reach past the interface, or coupling leaks across seams.
   - The **deletion test** says complexity would spread back to callers.

3. **Present candidates as an HTML report.** Follow [references/HTML-REPORT.md](references/HTML-REPORT.md). Write a self-contained HTML file to the OS temp directory — nothing lands in the repo. Each candidate includes involved modules, the actual friction, the deepening direction, leverage / locality / test benefit, a before / after diagram, and recommendation strength `Strong | Worth exploring | Speculative`.

4. **Wait for a pick.** Show the report path and the top recommendation. Do not propose interfaces yet. After the user picks, use `grilling` to walk constraints, dependencies, the target module, seam, and tests. `grilling` keeps the glossary and necessary ADRs current through domain-modeling.

5. **Go deeper only as needed.** When dependency categories get involved, read `../codebase-design/DEEPENING.md`. When the user wants alternatives, or one design is not enough to judge, read `../codebase-design/DESIGN-IT-TWICE.md`.

This mode investigates and reports. It does not change product code. A requirement contract goes to `to-spec`. Shared design across several implementations goes to `high-level-design`, then `quick-implement` or `loop` by scope.
