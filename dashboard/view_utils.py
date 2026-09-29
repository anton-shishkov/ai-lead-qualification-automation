"""Small, dependency-free helpers for dashboard filtering and CSV download."""
import csv
import io


def filter_leads(rows, priorities, search):
    query = search.strip().casefold()
    filtered = [row for row in rows if row["priority"] in priorities and query in
                f"{row['company_name']} {row['first_name']} {row['last_name']}".casefold()]
    return sorted(filtered, key=lambda row: (-row["final_score"], row["company_name"]))


def export_csv(rows, columns):
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")
