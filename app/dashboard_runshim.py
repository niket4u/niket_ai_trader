import os, json, glob
from flask import Flask, jsonify, render_template_string

PORT = int(os.getenv("DASHBOARD_PORT", "8080"))
LOG_DIR = os.getenv("LOG_DIR", "/tmp/niketbot_logs")
STATE_PATH = os.path.join(LOG_DIR, "state.json")
ALERTS_PATH = os.path.join(LOG_DIR, "alerts.json")

app = Flask(__name__)

def _load_json(path, default):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return default

def _tail_log(n=200):
    try:
        files = sorted(glob.glob(os.path.join(LOG_DIR, "*.log")), reverse=True)
        if not files:
            return []
        with open(files[0], "r", encoding="utf-8", errors="ignore") as f:
            return f.readlines()[-n:]
    except Exception:
        return []

@app.route("/api/health")
def api_health():
    st = _load_json(STATE_PATH, {})
    return jsonify({
        "ok": True,
        "mode": st.get("mode", os.getenv("MODE","paper")),
        "last_run_utc": st.get("last_run_utc"),
        "caps": st.get("caps", {}),
        "positions": st.get("positions", {}),
    })

@app.route("/")
def home():
    st = _load_json(STATE_PATH, {})
    alerts = _load_json(ALERTS_PATH, [])
    lines = _tail_log()
    html = """
    <!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <title>NiketBot (Shim)</title></head><body style="font-family:system-ui;padding:16px">
    <h2>NiketBot Dashboard (Shim)</h2>
    <p>Port: {{port}} | Log dir: {{logdir}}</p>
    <h3>State</h3><pre>{{st|tojson(indent=2)}}</pre>
    <h3>Alerts</h3><pre>{{alerts|tojson(indent=2)}}</pre>
    <h3>Log tail</h3><pre>{% for ln in lines %}{{ln}}{% endfor %}</pre>
    </body></html>
    """
    return render_template_string(html, st=st, alerts=alerts, lines=lines, port=PORT, logdir=LOG_DIR)

def run():
    app.run(host="0.0.0.0", port=PORT, debug=False)
