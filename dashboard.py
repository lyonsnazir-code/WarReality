import json
from pathlib import Path
from flask import Flask, render_template_string

app = Flask(__name__)
LEDGER_FILE = Path("knowledge_graph.json")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>WarReality Genesis OS - Command Dashboard</title>
    <meta http-equiv="refresh" content="3">
    <style>
        body { background-color: #0f172a; color: #f8fafc; font-family: monospace; padding: 20px; }
        h1 { color: #38bdf8; text-transform: uppercase; letter-spacing: 2px; }
        .card { background: #1e293b; border: 1px: solid #334155; padding: 15px; margin-bottom: 15px; border-radius: 6px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .metric { font-size: 1.2em; color: #4ade80; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border: 1px solid #334155; padding: 8px; text-align: left; }
        th { background: #0f172a; color: #38bdf8; }
    </style>
</head>
<body>
    <h1>WarReality // Genesis Node 00 Dashboard</h1>
    <p>Status: <span style="color: #4ade80; font-weight: bold;">ONLINE & AUTONOMOUS</span></p>
    
    <div class="card">
        <h3>System Metrics</h3>
        <p class="metric">Total Telemetry Blocks Logged: {{ total_entries }}</p>
        <p>Active Wallet: <code>Configured via .env</code></p>
    </div>

    <div class="card">
        <h3>Live Event Ledger (Last 5 Entries)</h3>
        <table>
            <tr>
                <th>Timestamp</th>
                <th>Anomalies</th>
                <th>Intelligence Vector</th>
            </tr>
            {% for entry in recent_entries %}
            <tr>
                <td>{{ entry.timestamp }}</td>
                <td>{{ entry.anomalies }}</td>
                <td>{{ entry.intel[0].title if entry.intel else 'No intel captured' }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    data = []
    if LEDGER_FILE.exists():
        try:
            with open(LEDGER_FILE, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []
            
    recent_entries = data[-5:][::-1] if data else []
    return render_template_string(HTML_TEMPLATE, total_entries=len(data), recent_entries=recent_entries)

if __name__ == "__main__":
    print("[DASHBOARD] Launching local command UI at http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)