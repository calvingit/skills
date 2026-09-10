"""Translate the human review report at the runtime boundary; never infer a pass."""

from __future__ import annotations

import re
from typing import Any

SECTIONS = ("Verdict", "Scope", "Findings", "Follow-up", "Requirement gaps", "Unverified", "Evidence")
REPORT_CONTRACT = {
    "format": "Markdown, not JSON; no enclosing code fence",
    "sections": list(SECTIONS),
    "verdict": ["PASS", "FIXES NEEDED", "INCOMPLETE"],
    "empty_sections": "Use exactly None. for empty Findings, Follow-up, Requirement gaps, and Unverified.",
    "findings": "Each Findings/Follow-up entry: ### [P0|P1|P2|P3] title, then location, trigger, impact, correction and verification in prose.",
    "language": "Keep headings and verdict values as specified; write explanations in the user's language.",
    "decision": "PASS requires no Findings, Requirement gaps or Unverified. FIXES NEEDED requires Findings and no gaps. INCOMPLETE requires Requirement gaps or Unverified. Describe actual scope and evidence; retain failed required verification.",
}


def normalize_review_report(report: str) -> dict[str, Any]:
    """Malformed or contradictory reports block for clarification instead of retrying code."""
    try:
        sections = _sections(report)
        verdict = sections["Verdict"]
        findings = _findings(sections["Findings"], "change_defect", "retry")
        follow_up = _findings(sections["Follow-up"], "follow_up", "new-ticket")
        gaps = sections["Requirement gaps"] != "None."
        unverified = sections["Unverified"] != "None."
        expected = "INCOMPLETE" if gaps or unverified else "FIXES NEEDED" if findings else "PASS"
        if verdict != expected:
            raise ValueError("Verdict contradicts the findings or missing evidence.")
        return {
            "outcome": "completed",
            "payload": {
                "review_report": report,
                # These fields belong to the existing receipt schema, not the reviewer.
                "review": {
                    "contract": "failed" if gaps or unverified else "pass",
                    "change_surface": "failed" if findings or unverified else "pass",
                    "exploratory": "pass",
                    "protocol_health": "gap" if gaps else "not_triggered",
                },
                "blocking_findings": findings,
                "non_blocking_findings": follow_up,
                "acceptance_protocol_gaps": [{
                    "category": "requirement_gap", "severity": "P2",
                    "evidence": sections["Requirement gaps"], "recommended_route": "clarify",
                }] if gaps else [],
                "unverified_scope": [{"scope": sections["Scope"], "reason": sections["Unverified"]}] if unverified else [],
            },
        }
    except ValueError as exc:
        return {
            "outcome": "blocked",
            "payload": {
                "review_report": report,
                "blocker": {
                    "category": "external",
                    "reason": f"Review report cannot be accepted: {exc}",
                    "release_condition": "Obtain a complete, consistent Markdown review of the same scope and evidence.",
                },
            },
        }


def _sections(report: str) -> dict[str, str]:
    headings = list(re.finditer(r"^## ([^\n]+)\s*$", report, re.MULTILINE))
    if [match.group(1).strip() for match in headings] != list(SECTIONS):
        raise ValueError("Required review sections are missing, duplicated, or out of order.")
    if report[:headings[0].start()].strip():
        raise ValueError("Unexpected text before the report.")
    sections = {
        match.group(1).strip(): report[match.end():headings[index + 1].start() if index + 1 < len(headings) else len(report)].strip()
        for index, match in enumerate(headings)
    }
    if any(not body for body in sections.values()):
        raise ValueError("Review sections must not be empty.")
    if any(sections[key] == "None." for key in ("Scope", "Evidence")):
        raise ValueError("Scope and evidence must describe the review performed.")
    return sections


def _findings(body: str, category: str, route: str) -> list[dict[str, str]]:
    if body == "None.":
        return []
    entries = list(re.finditer(r"^### \[(P[0-3])\] (\S[^\n]*)$", body, re.MULTILINE))
    if not entries or body[:entries[0].start()].strip():
        raise ValueError("Findings need a severity, title, and supporting explanation.")
    findings = []
    for index, entry in enumerate(entries):
        end = entries[index + 1].start() if index + 1 < len(entries) else len(body)
        if not body[entry.end():end].strip():
            raise ValueError("A finding has no supporting explanation.")
        findings.append({"category": category, "severity": entry.group(1),
                         "evidence": body[entry.start():end].strip(), "recommended_route": route})
    return findings
