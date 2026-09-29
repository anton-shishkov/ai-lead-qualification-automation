"""Local lead-qualification dashboard. Launch with streamlit run dashboard/app.py."""
import csv
from html import escape
from pathlib import Path

import streamlit as st

from dashboard.view_utils import export_csv, filter_leads

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "qualified_leads.csv"
RAW = ROOT / "data" / "sample_leads.csv"

st.set_page_config(page_title="Lead Intelligence | Portfolio Demo", page_icon="◈", layout="wide")
st.markdown("""<style>
:root {color-scheme: light}
.stApp {background: #f5f7f9; color: #192c3b}
.block-container {max-width: 1320px; padding: 1.45rem 2rem 3rem}
h1, h2, h3 {color: #183246; letter-spacing: -.025em}
h1 {font-size: clamp(1.8rem, 3vw, 2.45rem) !important; margin-bottom: .15rem !important}
h3 {font-size: 1.15rem !important}
.eyebrow {font-size: .72rem; font-weight: 800; letter-spacing: .13em; color: #52758a; text-transform: uppercase; margin-bottom: .25rem}
.subhead {color: #657988; font-size: .91rem; margin-bottom: 1.2rem}
.pipeline {display: flex; align-items: center; flex-wrap: wrap; gap: .48rem; padding: .75rem 1rem;
    background: #eaf1f5; border: 1px solid #d5e2e9; border-radius: 10px; color: #31566a;
    font-size: .85rem; font-weight: 600; margin: .35rem 0 1.15rem}
.pipeline .arrow {color: #92a9b6; padding: 0 .18rem}
[data-testid="stMetric"] {background: #fff; border: 1px solid #dce5ea; border-radius: 12px;
    padding: .78rem .9rem; box-shadow: 0 2px 9px rgba(24,50,70,.035); min-height: 94px}
[data-testid="stMetricLabel"] {font-size: .76rem; color: #607485; font-weight: 650}
[data-testid="stMetricValue"] {font-size: clamp(1.25rem, 2vw, 1.65rem); color: #183246; font-weight: 730}
[data-testid="stVerticalBlockBorderWrapper"] {border-color: #dce5ea !important; border-radius: 12px !important; background: #fff}
.section-kicker {font-size: .72rem; text-transform: uppercase; letter-spacing: .12em; font-weight: 800;
    color: #57788a; margin-bottom: .1rem}
.section-copy {color: #667b89; font-size: .84rem; margin-bottom: .55rem}
.priority-badge {display: inline-block; border-radius: 999px; padding: .2rem .62rem; font-size: .76rem;
    font-weight: 750; letter-spacing: .015em}
.priority-hot {background: #e5f2eb; color: #1c684e}
.priority-warm {background: #fbf1db; color: #875d19}
.priority-cold {background: #e8eef3; color: #4b6374}
.detail-label {font-size: .72rem; font-weight: 750; text-transform: uppercase; letter-spacing: .09em;
    color: #698090; margin-bottom: .18rem}
.detail-copy {color: #284253; line-height: 1.55; font-size: .91rem; margin-bottom: .92rem}
.message-card {background: #f0f5f7; border: 1px solid #d9e6eb; border-left: 3px solid #4a8192;
    border-radius: 9px; padding: 1rem 1.1rem; color: #203c4b; line-height: 1.65; font-size: .94rem;
    white-space: pre-wrap}
.card-note {color: #718593; font-size: .76rem; margin-top: .6rem}
@media (max-width: 800px) {.block-container {padding: 1rem .9rem 2rem} [data-testid="stMetric"] {min-height: 82px}}
</style>""", unsafe_allow_html=True)

st.markdown('<div class="eyebrow">Revenue operations / lead intelligence</div>', unsafe_allow_html=True)
st.title("AI Lead Qualification")
st.markdown('<div class="subhead">A local portfolio demo using fictional B2B contacts and deterministic mock AI.</div>', unsafe_allow_html=True)

if not DATA.exists():
    st.warning("No qualified leads yet. Run `python -m scripts.process_leads` from the project folder, then refresh.")
    st.stop()

with DATA.open(newline="", encoding="utf-8-sig") as handle:
    rows = list(csv.DictReader(handle))
if not rows:
    st.warning("The results file is empty. Run the processor again.")
    st.stop()

for row in rows:
    row["final_score"] = int(row["final_score"])

raw_count = None
if RAW.exists():
    with RAW.open(newline="", encoding="utf-8-sig") as handle:
        raw_count = sum(1 for _ in csv.DictReader(handle))
pipeline_start = f"{raw_count} raw records" if raw_count is not None else "Raw records"
st.markdown(
    f'<div class="pipeline"><span>{pipeline_start}</span><span class="arrow">→</span>'
    f'<span>{len(rows)} unique leads</span><span class="arrow">→</span>'
    '<span>AI-qualified automatically</span></div>', unsafe_allow_html=True)

average = sum(r["final_score"] for r in rows) / len(rows)
metrics = [("Total Leads", len(rows)), ("Hot", sum(r["priority"] == "Hot" for r in rows)),
           ("Warm", sum(r["priority"] == "Warm" for r in rows)),
           ("Cold", sum(r["priority"] == "Cold" for r in rows)), ("Average Score", f"{average:.1f}")]
for col, (label, value) in zip(st.columns(5, gap="small"), metrics):
    with col:
        st.metric(label, value)

st.write("")
st.markdown('<div class="section-kicker">Lead queue</div>', unsafe_allow_html=True)
st.subheader("Ranked leads")
filter_col, search_col, export_col = st.columns([2, 2, 1.15], gap="medium")
with filter_col:
    selected = st.multiselect("Priority", ["Hot", "Warm", "Cold"], default=["Hot", "Warm", "Cold"])
with search_col:
    search = st.text_input("Search company or contact", placeholder="Company or contact name")

filtered = filter_leads(rows, selected, search)
with export_col:
    st.markdown('<div style="height: 1.75rem"></div>', unsafe_allow_html=True)
    st.download_button("Export filtered CSV", export_csv(filtered, list(rows[0])),
                       file_name="qualified_leads_filtered.csv", mime="text/csv",
                       width="stretch", disabled=not filtered)

st.markdown(f'<div class="section-copy">{len(filtered)} of {len(rows)} leads shown · select a lead below for the full assessment.</div>', unsafe_allow_html=True)
view = [{"Score": r["final_score"], "Priority": r["priority"], "Company": r["company_name"],
         "Contact": f"{r['first_name']} {r['last_name']}".strip(), "Title": r["job_title"],
         "Industry": r["industry"], "Job Function": r["job_function"]}
        for r in filtered]

if view:
    import pandas as pd  # Streamlit already depends on pandas; used only for restrained cell styling.

    palette = {"Hot": "background-color: #e5f2eb; color: #1c684e; font-weight: 700",
               "Warm": "background-color: #fbf1db; color: #875d19; font-weight: 700",
               "Cold": "background-color: #e8eef3; color: #4b6374; font-weight: 700"}
    styled = pd.DataFrame(view).style.map(lambda value: palette.get(value, ""), subset=["Priority"])
    st.dataframe(styled, width="stretch", hide_index=True, height=min(470, 40 + len(view) * 35),
                 column_config={"Score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100, format="%d")})
else:
    st.info("No leads match these filters. Adjust the priority or search term.")

if filtered:
    st.write("")
    st.markdown('<div class="section-kicker">Selected lead</div>', unsafe_allow_html=True)
    st.subheader("Qualification & outreach")
    labels = [f"{r['company_name']} — {r['first_name']} {r['last_name']}" for r in filtered]
    choice = st.selectbox("Choose a lead", options=range(len(filtered)),
                          format_func=lambda index: labels[index])
    lead = filtered[choice]
    details, outreach = st.columns([1, 1.2], gap="medium")
    with details:
        with st.container(border=True):
            heading, badge = st.columns([3, 1], vertical_alignment="center")
            with heading:
                st.markdown(f"### {escape(lead['company_name'])}")
                st.caption(f"{lead['first_name']} {lead['last_name']} · {lead['job_title'] or 'Title unavailable'}")
            with badge:
                priority_name = lead["priority"]
                st.markdown(f'<span class="priority-badge priority-{priority_name.lower()}">{priority_name}</span>', unsafe_allow_html=True)
            st.metric("Final score", f"{lead['final_score']} / 100")
            st.markdown('<div class="detail-label">Qualification reason</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="detail-copy">{escape(lead["qualification_reason"])}</div>', unsafe_allow_html=True)
            if lead["validation_status"] == "Incomplete":
                st.caption(f"Incomplete record · missing: {lead['missing_fields']}")
    with outreach:
        with st.container(border=True):
            st.markdown("### Outreach preview")
            st.caption("Suggested first touch · review before sending")
            st.markdown('<div class="detail-label">Personalized opening</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="message-card">{escape(lead["personalized_opening"])}</div>', unsafe_allow_html=True)
            st.markdown('<div class="card-note">Select the text above to copy it into your outreach tool.</div>', unsafe_allow_html=True)
            st.write("")
            st.markdown('<div class="detail-label">Outreach angle</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="detail-copy">{escape(lead["outreach_angle"])}</div>', unsafe_allow_html=True)

st.write("")
st.markdown('<div class="section-kicker">Pipeline composition</div>', unsafe_allow_html=True)
st.subheader("Lead mix")
chart_cols = st.columns(2, gap="medium")
for col, field, heading in ((chart_cols[0], "industry", "By industry"),
                            (chart_cols[1], "job_function", "By job function")):
    counts = {}
    for row in filtered:
        key = row[field] or "Unknown"
        counts[key] = counts.get(key, 0) + 1
    with col:
        with st.container(border=True):
            st.markdown(f"**{heading}**")
            if counts:
                ordered = dict(sorted(counts.items(), key=lambda pair: pair[1], reverse=True))
                st.bar_chart(ordered, horizontal=True, color="#447d8b")
            else:
                st.caption("No leads match the current filter.")
