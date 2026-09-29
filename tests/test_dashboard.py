import csv
import io
import unittest
from pathlib import Path

from dashboard.view_utils import export_csv, filter_leads


ROOT = Path(__file__).resolve().parents[1]


class DashboardViewTests(unittest.TestCase):
    def setUp(self):
        with (ROOT / "data" / "qualified_leads.csv").open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            self.columns = reader.fieldnames
            self.rows = list(reader)
        for row in self.rows:
            row["final_score"] = int(row["final_score"])

    def test_filter_search_and_export_roundtrip(self):
        leads = filter_leads(self.rows, ["Hot"], "ridgewell")
        self.assertEqual(len(leads), 1)
        self.assertEqual(leads[0]["company_name"], "Ridgewell Motion Systems")
        exported = list(csv.DictReader(io.StringIO(export_csv(leads, self.columns).decode("utf-8"))))
        self.assertEqual(len(exported), 1)
        self.assertEqual(list(exported[0]), self.columns)
        self.assertEqual(exported[0]["company_name"], leads[0]["company_name"])
        self.assertEqual(exported[0]["personalized_opening"], leads[0]["personalized_opening"])

    def test_priority_filter_preserves_score_order(self):
        leads = filter_leads(self.rows, ["Warm"], "")
        self.assertTrue(leads)
        self.assertTrue(all(row["priority"] == "Warm" for row in leads))
        self.assertEqual([r["final_score"] for r in leads],
                         sorted((r["final_score"] for r in leads), reverse=True))


if __name__ == "__main__":
    unittest.main()
