import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.ai_provider import mock_qualify
from scripts.process_leads import OUTPUT_COLUMNS, ROOT, process_file, process_rows
from scripts.scoring import normalize, priority, score


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.sample = ROOT / "data" / "sample_leads.csv"

    def test_score_range_and_breakdown(self):
        with self.sample.open(newline="", encoding="utf-8") as handle:
            for raw in csv.DictReader(handle):
                baseline, parts = score(normalize(raw))
                self.assertTrue(0 <= baseline <= 100)
                self.assertEqual(baseline, sum(parts.values()))

    def test_thresholds(self):
        self.assertEqual([priority(x) for x in (0, 54, 55, 79, 80, 100)],
                         ["Cold", "Cold", "Warm", "Warm", "Hot", "Hot"])

    def test_duplicates_and_missing_fields(self):
        with self.sample.open(newline="", encoding="utf-8") as handle:
            rows = process_rows(csv.DictReader(handle))
        self.assertEqual(len(rows), 24)
        self.assertEqual(sum(r["validation_status"] == "Incomplete" for r in rows), 4)
        self.assertTrue(any(r["missing_fields"] for r in rows))

    def test_mock_is_deterministic(self):
        row = normalize({"company_name": "Test Works", "first_name": "Ava", "job_title": "Procurement Director"})
        self.assertEqual(mock_qualify(row, 65), mock_qualify(row, 65))

    def test_malformed_live_response_falls_back(self):
        raw = {"company_name": "Test Works", "website": "test.example", "first_name": "Ava",
               "last_name": "Lee", "job_title": "Procurement Director", "country": "US",
               "industry": "Manufacturing", "employee_count": "100"}
        rows = process_rows([raw], mode="live", provider=lambda *_: "not json")
        self.assertEqual(rows[0]["ai_source"], "mock_fallback")
        self.assertTrue(rows[0]["personalized_opening"])

    def test_file_output_schema(self):
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder) / "results.csv"
            rows = process_file(self.sample, out)
            with out.open(newline="", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                self.assertEqual(reader.fieldnames, OUTPUT_COLUMNS)
                self.assertEqual(len(list(reader)), len(rows))
            self.assertTrue(all(0 <= r["final_score"] <= 100 for r in rows))

    def test_bad_header_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "bad.csv"
            source.write_text("company_name\nA\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                process_file(source, Path(folder) / "out.csv")

    def test_n8n_export_structure_and_no_credentials(self):
        path = ROOT / "n8n" / "lead_qualification_workflow.json"
        workflow = json.loads(path.read_text(encoding="utf-8"))
        names = {node["name"] for node in workflow["nodes"]}
        self.assertTrue(any(node["type"] == "n8n-nodes-base.manualTrigger" for node in workflow["nodes"]))
        self.assertTrue(any(node["type"] == "n8n-nodes-base.httpRequest" for node in workflow["nodes"]))
        self.assertFalse(any(node["type"] == "n8n-nodes-base.executeCommand" for node in workflow["nodes"]))
        self.assertFalse(any("credentials" in node for node in workflow["nodes"]))
        for source, branches in workflow["connections"].items():
            self.assertIn(source, names)
            for branch in branches["main"]:
                for edge in branch:
                    self.assertIn(edge["node"], names)


if __name__ == "__main__":
    unittest.main()
