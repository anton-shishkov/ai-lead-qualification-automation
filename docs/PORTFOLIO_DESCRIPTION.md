# AI Lead Qualification & Enrichment Automation

**Short description**

This portfolio demo shows how a raw B2B lead list can become a prioritized, review-ready pipeline. A local Python workflow cleans and validates CSV records, removes duplicate contacts, scores each lead against a defined industrial-services ICP, and produces concise qualification and outreach text. A deterministic mock AI mode makes the entire experience repeatable without paid APIs, while a separate provider interface supports a real LLM later. An n8n canvas provides a one-click local run, and a Streamlit dashboard presents KPI cards, ranked leads, filters, distribution charts, and CSV export. All companies and contacts are fictional; this is a demonstration project, not a client delivery.

## Problem

Raw lead spreadsheets mix strong prospects with poor fits, incomplete records, and duplicates. Reviewing them manually slows outreach and obscures why a lead deserves attention.

## Solution

A transparent scoring engine ranks contacts against a specified ICP, while a replaceable AI layer adds short, grounded qualification and outreach copy. Failed or malformed live AI responses fall back to safe mock output.

## Workflow

Import CSV → normalize and validate → deduplicate → score six ICP dimensions → generate structured AI assessment → bound the final score → export CSV → review in dashboard.

## Key Features

- Explainable 0–100 scoring and Hot/Warm/Cold thresholds.
- Deterministic, subscription-free mock mode.
- Incomplete-record flags and duplicate handling.
- Personalized opening and outreach angle for each retained contact.
- Local n8n trigger, interactive dashboard, and CSV export.

## Technology

Python standard library, Streamlit, n8n Community Edition, CSV, and an optional OpenAI-compatible API integration point.

## Business Value

The demo illustrates faster lead triage, clearer prioritization, and more consistent first-touch preparation. It also shows how a team could inspect scoring decisions before using them operationally.

