# Import and run the n8n demo

The workflow is a local orchestration layer over the tested Python processor. It uses a fixed HTTP Request to a loopback-only Python service, plus a Code node that checks the returned summary. Validation, scoring, mock AI, and classification stay in the Python modules, so n8n and command-line runs produce the same CSV. There are no credentials, API keys, or shell-command nodes in the export.

1. In PowerShell at the project root, run `.\.venv\Scripts\python.exe -m scripts.local_api`. Leave this terminal open. Check `http://127.0.0.1:8765/health` if needed.
2. In a second PowerShell terminal, run `npx n8n` (or the installed n8n binary). Open `http://localhost:5678` and complete local owner setup if prompted.
3. Create a workflow and choose **Import from File**. Select `n8n/lead_qualification_workflow.json`.
4. Inspect the connected **01 Input → 02–07 Processing → 08 Output** nodes and their notes. Click **Execute workflow**.
5. The final node should report 26 input records, 24 unique leads, 2 duplicates removed, 4 incomplete records, and Hot/Warm/Cold counts. Check `data/qualified_leads.csv`, then refresh the Streamlit dashboard.

If the HTTP node says connection refused, start or restart the local bridge and verify `/health`. The bridge binds to `127.0.0.1:8765`, so n8n must run on the same host. A Docker-hosted n8n instance cannot use that address to reach the Windows host without changing the URL and network configuration. If port 8765 is occupied, stop the conflicting service before starting the bridge. The bridge's `/run` route accepts only POST requests with `X-Demo-Action: qualify`; the marker is not a secret.

The workflow deliberately uses mock mode so the recording is repeatable without external APIs. The service has no configurable input path and never runs a shell command.
