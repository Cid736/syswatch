from flask import Flask, render_template_string, jsonify, redirect, request, abort
from monitor import snapshot, check_thresholds
import threading, time, os, yaml, socket
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
app    = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(32))
CONFIG = Path(__file__).parent / "config.yml"
HOSTNAME = socket.gethostname()
CONTROL_TOKEN = os.environ.get('CONTROL_TOKEN', '')

if not CONTROL_TOKEN:
    raise RuntimeError("CONTROL_TOKEN must be set in .env before starting syswatch")


def _check_control():
    if request.form.get('token') != CONTROL_TOKEN:
        abort(403)

history: list[dict] = []
latest:  dict       = {}
HISTORY_MAX = 60

_stop_event = threading.Event()
_collector_thread: threading.Thread | None = None
collector_status = "running"


def load_cfg() -> dict:
    if CONFIG.exists():
        with open(CONFIG) as f:
            return yaml.safe_load(f) or {}
    return {}


def collector():
    global latest
    while not _stop_event.is_set():
        try:
            snap = snapshot(cpu_interval=1.0)
            latest = snap
            history.append(snap)
            if len(history) > HISTORY_MAX:
                history.pop(0)
        except Exception as e:
            print(f'[syswatch] collector error: {e}')
        _stop_event.wait(10)


def start_collector():
    global _collector_thread, _stop_event, collector_status
    _stop_event = threading.Event()
    _collector_thread = threading.Thread(target=collector, daemon=True)
    _collector_thread.start()
    collector_status = "running"


def stop_collector():
    global collector_status
    _stop_event.set()
    collector_status = "stopped"


TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>syswatch</title>
  <style>
    * { box-sizing:border-box; margin:0; padding:0; }
    body { font-family:'Segoe UI',sans-serif; background:#0d1117; color:#c9d1d9; }
    header { padding:20px 32px; border-bottom:1px solid #21262d; display:flex; align-items:center; gap:12px; flex-wrap:wrap; }
    header h1 { font-size:1.15rem; font-weight:600; color:#e6edf3; }
    .controls { display:flex; gap:8px; margin-left:auto; align-items:center; }
    .status-dot { width:8px; height:8px; border-radius:50%; display:inline-block; margin-right:6px; }
    .status-dot.running { background:#3fb950; box-shadow:0 0 6px #3fb950; }
    .status-dot.stopped { background:#f85149; }
    .status-label { font-size:0.78rem; color:#8b949e; margin-right:8px; }
    button { padding:6px 14px; border-radius:6px; border:none; font-size:0.78rem; font-weight:600; cursor:pointer; transition:opacity .15s; }
    button:hover { opacity:.8; }
    .btn-start   { background:#1a3a1f; color:#3fb950; border:1px solid #3fb950; }
    .btn-stop    { background:#3a1a1a; color:#f85149; border:1px solid #f85149; }
    .btn-restart { background:#1a2a3a; color:#58a6ff; border:1px solid #58a6ff; }
    .refresh-note { font-size:0.72rem; color:#484f58; margin-left:8px; }
    .cards { display:grid; grid-template-columns:repeat(auto-fill,minmax(220px,1fr)); gap:16px; padding:24px 32px; }
    .card { background:#161b22; border:1px solid #21262d; border-radius:10px; padding:20px; }
    .card h3 { font-size:0.78rem; color:#8b949e; text-transform:uppercase; letter-spacing:.5px; margin-bottom:10px; }
    .card .value { font-size:2rem; font-weight:700; }
    .card .sub { font-size:0.78rem; color:#8b949e; margin-top:4px; }
    .bar-wrap { background:#21262d; border-radius:4px; height:6px; margin-top:10px; overflow:hidden; }
    .bar { height:6px; border-radius:4px; }
    .green  { color:#3fb950; } .bar.green  { background:#3fb950; }
    .yellow { color:#d29922; } .bar.yellow { background:#d29922; }
    .red    { color:#f85149; } .bar.red    { background:#f85149; }
    .alerts { margin:0 32px 16px; }
    .alert-box { background:#2a1a00; border:1px solid #6b3f00; border-radius:8px; padding:10px 16px; font-size:0.82rem; color:#e09a3a; }
    .alert-box.ok { background:#0d2218; border-color:#1a4a2e; color:#3fb950; }
    .section { padding:0 32px 32px; }
    .section h2 { font-size:0.82rem; color:#8b949e; text-transform:uppercase; letter-spacing:.5px; margin-bottom:12px; }
    table { width:100%; border-collapse:collapse; font-size:0.8rem; }
    th { text-align:left; padding:8px 10px; color:#8b949e; border-bottom:1px solid #21262d; font-weight:500; }
    td { padding:7px 10px; border-bottom:1px solid #161b22; font-variant-numeric:tabular-nums; }
    .thresh { font-size:0.72rem; color:#484f58; margin-top:6px; }
    footer { text-align:center; padding:16px; font-size:0.72rem; color:#484f58; }
    .alpha-banner { background:#1a1200; border-bottom:1px solid #4a3500; padding:6px 32px; font-size:0.75rem; color:#d29922; display:flex; align-items:center; gap:8px; }
    .alpha-badge  { background:#4a3500; color:#d29922; font-size:0.65rem; font-weight:700; padding:1px 7px; border-radius:4px; letter-spacing:.5px; }
  </style>
</head>
<body>

<header>
  <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="#3fb950" stroke-width="2">
    <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
  </svg>
  <h1>syswatch &mdash; {{ hostname }}</h1>
  <div class="controls">
    <span class="status-label">
      <span class="status-dot {{ collector_status }}"></span>
      collector {{ collector_status }}
    </span>
    <form method="post" action="/control/start"   style="display:inline"><button class="btn-start">&#9654; Start</button></form>
    <form method="post" action="/control/stop"    style="display:inline"><button class="btn-stop">&#9646;&#9646; Stop</button></form>
    <form method="post" action="/control/restart" style="display:inline"><button class="btn-restart">&#8635; Restart</button></form>
    <span class="refresh-note">page auto-refresh 15s</span>
  </div>
</header>

<div class="alpha-banner">
  <span class="alpha-badge">ALPHA</span>
  Versión en desarrollo — pueden existir errores. Reporta cualquier problema en <a href="https://github.com/Cid736/syswatch/issues" target="_blank" style="color:#d29922;">github.com/Cid736/syswatch</a>
</div>

{% if alerts %}
<div class="alerts" style="margin-top:16px;">
  <div class="alert-box">&#9888; {{ alerts | join(' &nbsp;|&nbsp; ') }}</div>
</div>
{% else %}
<div class="alerts" style="margin-top:16px;">
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

<script>setTimeout(() => location.reload(), 15000);</script>
</body>
</html>"""


@app.route("/")
def index():
    cfg    = load_cfg()
    snap   = latest if latest else snapshot()
    alerts = check_thresholds(snap, cfg)
    return render_template_string(
        TEMPLATE,
        snap=snap,
        cfg=cfg,
        alerts=alerts,
        history=history,
        hostname=HOSTNAME,
        collector_status=collector_status,
    )


@app.route("/control/start", methods=["POST"])
def ctrl_start():
    _check_control()
    global _collector_thread
    if _collector_thread is None or not _collector_thread.is_alive():
        start_collector()
    return redirect("/")


@app.route("/control/stop", methods=["POST"])
def ctrl_stop():
    _check_control()
    stop_collector()
    return redirect("/")


@app.route("/control/restart", methods=["POST"])
def ctrl_restart():
    _check_control()
    stop_collector()
    time.sleep(0.3)
    start_collector()
    return redirect("/")


@app.route("/api/metrics", methods=["POST"])
def api_metrics():
    _check_control()
    return jsonify(latest if latest else snapshot())


if __name__ == "__main__":
    start_collector()
    time.sleep(1.5)
    PORT = int(os.environ.get("PORT", 8081))
    HOST = os.environ.get("HOST", "127.0.0.1")
    print(f"[syswatch] dashboard -> http://localhost:{PORT}")

    @app.after_request
    def security_headers(r):
        r.headers['X-Frame-Options'] = 'DENY'
        r.headers['X-Content-Type-Options'] = 'nosniff'
        r.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return r

    app.run(host=HOST, port=PORT)
