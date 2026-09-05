"""Read stable upstream authority IDs without interpreting their semantics."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from .contracts import (
    HLD_DECISION_RE, SPEC_ACCEPTANCE_RE, SPEC_REQUIREMENT_RE, problem,
)

def extract_ids(path: Path, pattern: re.Pattern[str]) -> tuple[set[str], list[str]]:
    values: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if match := pattern.match(line):
            values.append(match.group(1).upper())
    duplicates = sorted(value for value, count in Counter(values).items() if count > 1)
    return set(values), duplicates


def authority_index(
    task_dir: Path,
) -> tuple[dict[str, set[str]], list[dict[str, str]]]:
    problems: list[dict[str, str]] = []
    spec = task_dir / "SPEC.md"
    hld = task_dir / "HLD.md"
    index = {"requirements": set(), "spec_acceptance": set(), "design_decisions": set()}
    if not spec.is_file():
        return index, problems
    try:
        requirements, duplicate_requirements = extract_ids(spec, SPEC_REQUIREMENT_RE)
        acceptance, duplicate_acceptance = extract_ids(spec, SPEC_ACCEPTANCE_RE)
        index["requirements"] = requirements
        index["spec_acceptance"] = acceptance
        if not requirements:
            problems.append(problem("authority", "missing_spec_requirements", "SPEC.md has no stable R IDs.", path="SPEC.md"))
        if not acceptance:
            problems.append(problem("authority", "missing_spec_acceptance", "SPEC.md has no stable AC IDs.", path="SPEC.md"))
        for value in duplicate_requirements:
            problems.append(problem("authority", "duplicate_requirement", f"SPEC requirement ID is duplicated: {value}", path="SPEC.md"))
        for value in duplicate_acceptance:
            problems.append(problem("authority", "duplicate_spec_acceptance", f"SPEC Acceptance ID is duplicated: {value}", path="SPEC.md"))
        if hld.is_file():
            decisions, duplicate_decisions = extract_ids(hld, HLD_DECISION_RE)
            index["design_decisions"] = decisions
            if not decisions:
                problems.append(problem("authority", "missing_hld_decisions", "HLD.md has no stable D IDs.", path="HLD.md"))
            for value in duplicate_decisions:
                problems.append(problem("authority", "duplicate_design_decision", f"HLD decision ID is duplicated: {value}", path="HLD.md"))
    except (OSError, UnicodeError) as exc:
        problems.append(problem("authority", "unreadable_authority", str(exc)))
    return index, problems
