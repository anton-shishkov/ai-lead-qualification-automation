"""Transparent deterministic ICP scoring; all weights sum to 100."""
import re

WEIGHTS = {"geography": 20, "industry": 25, "company_size": 15,
           "seniority": 15, "job_function": 15, "data_completeness": 10}
REQUIRED = ("company_name", "website", "first_name", "last_name",
            "job_title", "country", "industry", "employee_count")


def job_function(title):
    t = title.lower()
    for name, terms in (
        ("Procurement", ("procurement", "sourcing")),
        ("Supply Chain", ("supply chain", "logistics")),
        ("Purchasing", ("purchasing", "buyer")),
        ("Operations", ("operations", "plant manager")),
        ("Human Resources", ("human resources", "people operations", "hr ", "hr manager")),
        ("Talent Acquisition", ("talent acquisition", "recruiting", "recruitment")),
    ):
        if any(term in t for term in terms):
            return name
    return "Other"


def normalize(raw):
    row = {key: " ".join(str(raw.get(key) or "").strip().split()) for key in REQUIRED}
    country = row["country"].casefold().replace(".", "")
    if country in {"us", "usa", "united states", "united states of america"}:
        row["country"] = "United States"
    if row["website"]:
        site = re.sub(r"^https?://", "", row["website"], flags=re.I)
        row["website"] = re.sub(r"/+$", "", site).lower()
    count = row["employee_count"].replace(",", "")
    row["employee_count"] = str(int(count)) if count.isdigit() and int(count) > 0 else ""
    row["job_function"] = job_function(row["job_title"])
    return row


def score(row):
    title = row["job_title"].lower()
    industry = row["industry"].lower()
    count = int(row["employee_count"]) if row["employee_count"] else 0
    geo = 20 if row["country"] == "United States" else (5 if row["country"] else 0)
    if any(s in industry for s in ("manufactur", "machinery", "equipment", "engineering", "industrial")):
        industry_points = 25
    elif any(s in industry for s in ("construction", "logistics", "distribution", "automation")):
        industry_points = 13
    else:
        industry_points = 3 if industry else 0
    size = 15 if 20 <= count <= 1000 else (7 if count else 0)
    seniority = 15 if any(s in title for s in ("chief", "vp", "vice president", "director", "head of", "owner", "president")) else (9 if any(s in title for s in ("manager", "lead", "supervisor")) else (3 if title else 0))
    function = 15 if row["job_function"] != "Other" else (3 if title else 0)
    completeness = round(10 * sum(bool(row[k]) for k in REQUIRED) / len(REQUIRED))
    parts = {"geography": geo, "industry": industry_points, "company_size": size,
             "seniority": seniority, "job_function": function, "data_completeness": completeness}
    assert all(0 <= parts[k] <= WEIGHTS[k] for k in WEIGHTS)
    return sum(parts.values()), parts


def priority(score_value):
    return "Hot" if score_value >= 80 else "Warm" if score_value >= 55 else "Cold"

