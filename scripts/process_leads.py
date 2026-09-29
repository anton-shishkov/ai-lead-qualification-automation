"""CSV lead qualification entry point. Run from repository root or any directory."""
import argparse
import csv
import json
import os
from pathlib import Path

from scripts.ai_provider import ADJUSTMENTS, qualify
from scripts.scoring import REQUIRED, normalize, priority, score

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_COLUMNS = list(REQUIRED) + ["job_function", "baseline_score", "score_breakdown",
    "ai_icp_assessment", "ai_source", "final_score", "priority", "qualification_reason",
    "outreach_angle", "personalized_opening", "validation_status", "missing_fields"]


def process_rows(raw_rows, mode="mock", provider=None):
    output, seen = [], set()
    for raw in raw_rows:
        row = normalize(raw)
        email = str(raw.get("email") or "").strip().lower()
        identity = (row["website"], row["first_name"].casefold(), row["last_name"].casefold())
        key = ("email", email) if email else ("identity",) + identity
        if key in seen and (email or (row["website"] and (row["first_name"] or row["last_name"]))):
            continue
        seen.add(key)
        missing = [k for k in REQUIRED if not row[k]]
        baseline, parts = score(row)
        ai, source = qualify(row, baseline, mode, provider)
        final = max(0, min(100, baseline + ADJUSTMENTS[ai["ai_icp_assessment"]]))
        row.update(baseline_score=baseline, score_breakdown=json.dumps(parts, sort_keys=True),
                   ai_icp_assessment=ai["ai_icp_assessment"], ai_source=source,
                   final_score=final, priority=priority(final),
                   qualification_reason=ai["qualification_reason"], outreach_angle=ai["outreach_angle"],
                   personalized_opening=ai["personalized_opening"],
                   validation_status="Incomplete" if missing else "Complete", missing_fields="; ".join(missing))
        output.append(row)
    return output


def process_file(input_path, output_path, mode="mock"):
    with Path(input_path).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or not {"company_name", "first_name", "last_name"}.issubset(reader.fieldnames):
            raise ValueError("CSV must contain company_name, first_name and last_name headers")
        rows = process_rows(reader, mode)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=str(ROOT / "data" / "sample_leads.csv"))
    parser.add_argument("--output", default=str(ROOT / "data" / "qualified_leads.csv"))
    parser.add_argument("--mode", choices=("mock", "live"), default=os.getenv("AI_MODE", "mock"))
    args = parser.parse_args()
    rows = process_file(args.input, args.output, args.mode)
    print(json.dumps({"input": args.input, "output": args.output, "unique_leads": len(rows),
                      "hot": sum(r["priority"] == "Hot" for r in rows),
                      "warm": sum(r["priority"] == "Warm" for r in rows),
                      "cold": sum(r["priority"] == "Cold" for r in rows)}))


if __name__ == "__main__":
    main()
