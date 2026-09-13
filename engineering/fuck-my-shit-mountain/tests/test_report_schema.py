import copy
import json
from pathlib import Path
import unittest

from jsonschema import Draft7Validator


SCHEMA = Path(__file__).resolve().parents[1] / "templates" / "audit-report.json"


class ReportSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        schema = json.loads(SCHEMA.read_text())
        Draft7Validator.check_schema(schema)
        cls.validator = Draft7Validator(schema)

    def setUp(self):
        self.report = {
            "metadata": {
                "project": "fixture-cli", "auditModes": ["full"],
                "date": "2026-09-13", "reviewer": "test fixture", "commitHash": "fixture",
            },
            "executiveSummary": {"text": "No findings in this synthetic review scope."},
            "findingStatistics": {"bySeverity": [], "total": {"count": 0, "confirmed": 0, "suspected": 0}},
            "projectMap": {"structure": "Internal CLI", "keyComponents": ["entrypoint"], "riskAreas": []},
            "coverageMatrix": [{"dimension": "architecture", "coverage": "High",
                                "evidenceInspected": "fixture entrypoint", "exclusions": "none in fixture"}],
            "topRisks": [], "detailedFindings": [],
        }
        self.finding = {
            "id": "F1", "title": "Retired command", "severity": "Low", "confidence": "High",
            "category": "Documentation", "status": "Confirmed", "affectedArea": "README usage",
            "evidence": {"file": "README.md", "functionOrModule": "usage", "relevantBehavior": "Removed command is documented"},
            "failureScenario": "Reader copies removed command", "userVisibleImpact": "Setup fails",
            "minimalFix": "Update example", "regressionTestSuggestion": "Compare with current CLI help",
        }

    def report_with_finding(self):
        report = copy.deepcopy(self.report)
        report["detailedFindings"] = [copy.deepcopy(self.finding)]
        report["findingStatistics"] = {
            "bySeverity": [{"severity": "Low", "count": 1, "confirmed": 1, "suspected": 0}],
            "total": {"count": 1, "confirmed": 1, "suspected": 0},
        }
        return report

    def test_zero_findings_without_scores_is_valid(self):
        self.validator.validate(self.report)

    def test_finding_without_effort_estimate_is_valid(self):
        self.validator.validate(self.report_with_finding())

    def test_missing_evidence_is_rejected(self):
        report = self.report_with_finding()
        del report["detailedFindings"][0]["evidence"]
        self.assertTrue(list(self.validator.iter_errors(report)))

    def test_requested_scores_and_estimate_remain_valid(self):
        report = self.report_with_finding()
        report["detailedFindings"][0]["estimatedEffort"] = "30 minutes"
        report["scoreDashboard"] = {
            "dimensions": [{"name": "Maintainability", "score": 8, "grade": "A", "justification": "One contained documentation issue"}],
            "overall": {"score": 8, "grade": "A"},
        }
        self.validator.validate(report)

    def test_invalid_score_is_rejected(self):
        report = copy.deepcopy(self.report)
        report["scoreDashboard"] = {"dimensions": [], "overall": {"score": 11, "grade": "A"}}
        self.assertTrue(list(self.validator.iter_errors(report)))


if __name__ == "__main__":
    unittest.main()
