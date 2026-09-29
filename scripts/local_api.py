"""Local-only HTTP bridge for the n8n demo. Start: python -m scripts.local_api."""
import csv
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from scripts.process_leads import ROOT, process_file

HOST = "127.0.0.1"
PORT = 8765
INPUT = ROOT / "data" / "sample_leads.csv"
OUTPUT = ROOT / "data" / "qualified_leads.csv"


def run_demo():
    with INPUT.open(newline="", encoding="utf-8-sig") as handle:
        input_records = sum(1 for _ in csv.DictReader(handle))
    rows = process_file(INPUT, OUTPUT, "mock")
    return {
        "status": "complete",
        "input_records": input_records,
        "unique_leads": len(rows),
        "duplicates_removed": input_records - len(rows),
        "incomplete": sum(row["validation_status"] == "Incomplete" for row in rows),
        "hot": sum(row["priority"] == "Hot" for row in rows),
        "warm": sum(row["priority"] == "Warm" for row in rows),
        "cold": sum(row["priority"] == "Cold" for row in rows),
        "ai_mode": "mock",
        "output": str(OUTPUT),
    }


class Handler(BaseHTTPRequestHandler):
    def send_json(self, status, payload):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/health":
            self.send_json(200, {"status": "ready", "service": "lead-demo"})
        else:
            self.send_json(404, {"error": "Not found"})

    def do_POST(self):
        if self.path != "/run":
            self.send_json(404, {"error": "Not found"})
            return
        if self.headers.get("X-Demo-Action") != "qualify":
            self.send_json(403, {"error": "Expected local demo action header"})
            return
        try:
            self.send_json(200, run_demo())
        except (OSError, ValueError, KeyError) as exc:
            self.send_json(500, {"error": str(exc)})


def main():
    server = HTTPServer((HOST, PORT), Handler)
    print(f"Lead demo API listening at http://{HOST}:{PORT}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
