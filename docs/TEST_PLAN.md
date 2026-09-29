# Test plan and verification

Run from the project root:

```powershell
python -m unittest discover -s tests -v
python -m scripts.process_leads
python -m compileall -q scripts dashboard
```

The automated tests cover score range and component sum, classification boundaries, duplicate removal, incomplete-record flags, deterministic mock output, malformed live-response fallback, required output columns, and invalid CSV headers. Inspect `data/qualified_leads.csv` after the processor runs. The sample should contain 26 raw rows and 24 unique output contacts, including four incomplete contacts. The final output should have no credentials or real contact data.

## Verified in the build environment (2026-09-28)

- Ten automated tests passed, including dashboard filter/order and CSV-export round-trip checks.
- The processor produced 24 unique rows from 26 raw records: 13 Hot, 7 Warm, 4 Cold, and four flagged incomplete records. Final scores ranged from 26 to 100.
- The loopback HTTP bridge returned a complete mock-mode summary from a real POST: 26 input records, 24 unique leads, 2 duplicates removed, 4 incomplete, and 13/7/4 Hot/Warm/Cold. A request without its expected action header returned HTTP 403. The bridge-generated CSV matched a direct Python pipeline run byte for byte (SHA-256).
- Streamlit 1.64.0 started and returned HTTP 200. Streamlit AppTest executed with zero exceptions, showed five KPI cards and two charts, and the Hot filter returned 13 ranked rows. Search narrowed results to one matching company; changing the selected lead updated its details and personalized opening; an empty search showed a clear no-results state. The dashboard export helper produced a one-row CSV with the full output schema and matching outreach text.
- The n8n JSON parsed, all connection targets resolved, no credential objects were present, and the workflow contains no Execute Command node. Import and canvas execution still require a completed local n8n installation.

Manual dashboard check: open Streamlit in a browser, sort the table, inspect the outreach preview, and download a filtered CSV. Manual n8n check: import the JSON on a local n8n installation, execute, and confirm its summary and output path. These exact UI interactions have not been claimed as verified.
