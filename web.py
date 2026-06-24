from flask import Flask, render_template_string, jsonify
from monitor import snapshot, check_thresholds
import threading, time, os, yaml
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
app    = Flask(__name__)
CONFIG = Path(__file__).parent / "config.yml"

history: list[dict] = []
latest:  dict       = {}
HISTORY_MAX = 60


def load_cfg() -> dict:
    if CONFIG.exists():
        with open(CONFIG) as f:
            return yaml.safe_load(f) or {}
    return {}


def collector():
    global latest
    while True:
        snap   = snapshot(cpu_interval=1.0)
        latest = snap
        history.append(snap)
        if len(history) > HISTORY_MAX:
            history.pop(0)
        time.sleep(10)


TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>syswatch</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Segoe UI', sans-serif; background: #0d1117; color: #c9d1d9; }
    header { padding: 20px 32px; border-bottom: 1px solid #21262d; display:flex; align-items:center; gap:12px; }
    header h1 { font-size:1.15rem; font-weight:600; color:#e6edf3; }
    header span { font-size:0.78rem; color:#8b949e; margin-left:auto; }
    .cards { display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:16px; padding:24px 32px; }
    .card { background:#161b22; border:1px solid #21262d; border-radius:10px; padding:20px; }
    .card h3 { font-size:0.78rem; color:#8b949e; text-transform:uppercase; letter-spacing:.5px; margin-bottom:10px; }
    .card .value { font-size:2rem; font-weight:700; }
    .card .sub { font-size:0.78rem; color:#8b949e; margin-top:4px; }
    .bar-wrap { background:#21262d; border-radius:4px; height:6px; margin-top:10px; overflow:hidden; }
    .bar { height:6px; border-radius:4px; transition: width .4s; }
    .green  { color:#3fb950; } .bar.green  { background:#3fb950; }
    .yellow { color:#d29922; } .bar.yellow { background:#d29922; }
    .red    { color:#f85149; } .bar.red    { background:#f85149; }
    .alerts { margin: 0 32px 16px; }
    .alert-box { background:#2a1a00; border:1px solid #6b3f00; border-radius:8px; padding:10px 16px; font-size:0.82rem; color:#e09a3a; }
    .alert-box.ok { background:#0d2218; border-color:#1a4a2e; color:#3fb950; }
    .section { padding: 0 32px 32px; }
    .section h2 { font-size:0.82rem; color:#8b949e; text-transform:uppercase; letter-spacing:.5px; margin-bottom:12px; }
    table { width:100%; border-collapse:collapse; font-size:0.8rem; }
    th { text-align:left; padding:8px 10px; color:#8b949e; border-bottom:1px solid #21262d; font-weight:500; }
    td { padding:7px 10px; border-bottom:1px solid #161b22; font-variant-numeric: tabular-nums; }
    footer { text-align:center; padding:16px; font-size:0.72rem; color:#484f58; }
    .thresh { font-size:0.72rem; color:#8b949e; margin-top:6px; }
  </style>
  <script>
    setTimeout(() => location.reload(), 15000);
  </script>
</head>
<body>

<header>
  <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="#3fb950" stroke-width="2">
    <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
  </svg>
  <h1>syswatch &mdash; {{ hostname }}</h1>
  <span>Auto-refresh 15s &nbsp;|&nbsp; {{ snap.ts }} UTC</span>
</header>

{% if alerts %}
<div class="alerts">
  <div class="alert-box">
    &#9888; Threshold breach: {{ alerts | join(' &nbsp;|&nbsp; ') }}
  </div>
</div>
{% else %}
<div class="alerts">
  <div class="alert-box ok">&#10003; All metrics within thresholds</div>
</div>
{% endif %}

<div class="cards">

  {% set cpu = snap.cpu %}
  {% set cpu_color = 'red' if cpu >= cfg.get('cpu_pct',90) else ('yellow' if cpu >= cfg.get('cpu_pct',90)*0.8 else 'green') %}
  <div class="card">
    <h3>CPU</h3>
    <div class="value {{ cpu_color }}">{{ "%.1f"|format(cpu) }}%</div>
    <div class="bar-wrap"><div class="bar {{ cpu_color }}" style="width:{{ cpu }}%"></div></div>
    <div class="thresh">Threshold: {{ cfg.get('cpu_pct',90) }}%</div>
  </div>

  {% set ram = snap.ram.used_pct %}
  {% set ram_color = 'red' if ram >= cfg.get('ram_pct',90) else ('yellow' if ram >= cfg.get('ram_pct',90)*0.8 else 'green') %}
  <div class="card">
    <h3>RAM</h3>
    <div class="value {{ ram_color }}">{{ "%.1f"|format(ram) }}%</div>
    <div class="sub">{{ snap.ram.used_gb }} / {{ snap.ram.total_gb }} GB</div>
    <div class="bar-wrap"><div class="bar {{ ram_color }}" style="width:{{ ram }}%"></div></div>
    <div class="thresh">Threshold: {{ cfg.get('ram_pct',90) }}%</div>
  </div>

  {% set disk = snap.disk.used_pct %}
  {% set disk_color = 'red' if disk >= cfg.get('disk_pct',85) else ('yellow' if disk >= cfg.get('disk_pct',85)*0.85 else 'green') %}
  <div class="card">
    <h3>Disk</h3>
    <div class="value {{ disk_color }}">{{ "%.1f"|format(disk) }}%</div>
    <div class="sub">{{ snap.disk.used_gb }} / {{ snap.disk.total_gb }} GB</div>
    <div class="bar-wrap"><div class="bar {{ disk_color }}" style="width:{{ disk }}%"></div></div>
    <div class="thresh">Threshold: {{ cfg.get('disk_pct',85) }}%</div>
  </div>

  {% set load1 = snap.load[0] %}
  {% set load_color = 'red' if load1 >= cfg.get('load_1m',4.0) else ('yellow' if load1 >= cfg.get('load_1m',4.0)*0.7 else 'green') %}
  <div class="card">
    <h3>Load avg</h3>
    <div class="value {{ load_color }}">{{ "%.2f"|format(load1) }}</div>
    <div class="sub">5m: {{ "%.2f"|format(snap.load[1]) }} &nbsp; 15m: {{ "%.2f"|format(snap.load[2]) }}</div>
    <div class="thresh">Threshold (1m): {{ cfg.get('load_1m',4.0) }}</div>
  </div>

  <div class="card">
    <h3>Network I/O</h3>
    <div class="value green" style="font-size:1.3rem;">{{ snap.net.sent_mb }} MB</div>
    <div class="sub">sent &nbsp;|&nbsp; recv {{ snap.net.recv_mb }} MB</div>
  </div>

</div>

<div class="section">
  <h2>History (last {{ history|length }} samples &mdash; every 10s)</h2>
  <table>
    <tr><th>Time (UTC)</th><th>CPU %</th><th>RAM %</th><th>Disk %</th><th>Load 1m</th></tr>
    {% for h in history|reverse %}
    <tr>
      <td>{{ h.ts }}</td>
      <td>{{ "%.1f"|format(h.cpu) }}</td>
      <td>{{ "%.1f"|format(h.ram.used_pct) }}</td>
      <td>{{ "%.1f"|format(h.disk.used_pct) }}</td>
      <td>{{ "%.2f"|format(h.load[0]) }}</td>
    </tr>
    {% endfor %}
  </table>
</div>

<footer>syswatch &mdash; github.com/Cid736/syswatch</footer>
</body>
</html>"""


@app.route("/")
def index():
    import socket
    cfg    = load_cfg()
    snap   = latest if latest else snapshot()
    alerts = check_thresholds(snap, cfg)
    return render_template_string(
        TEMPLATE,
        snap=snap,
        cfg=cfg,
        alerts=alerts,
        history=history,
        hostname=socket.gethostname(),
    )


@app.route("/api/metrics")
def api_metrics():
    return jsonify(latest if latest else snapshot())


if __name__ == "__main__":
    t = threading.Thread(target=collector, daemon=True)
    t.start()
    time.sleep(1.5)  # let first snapshot populate
    PORT = int(os.environ.get("PORT", 8081))
    print(f"[syswatch] dashboard -> http://localhost:{PORT}")
    app.run(host="0.0.0.0", port=PORT)
