
from flask import Flask, render_template, send_from_directory, request, Response, jsonify
import os, json, glob, datetime
from .config import settings

app = Flask(__name__, template_folder="templates", static_folder="static")

STATE_PATH = os.path.join(settings.log_dir, "state.json")

def check_auth(username, password):
    if not settings.dashboard_user:
        return True
    return username == settings.dashboard_user and password == settings.dashboard_pass

def authenticate():
    return Response('Authentication required', 401, {'WWW-Authenticate': 'Basic realm="NiketBot"'})

@app.before_request
def require_basic_auth():
    if not settings.dashboard_user:
        return None
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()

def tail_log(n_lines=200):
    month_files = sorted(glob.glob(os.path.join(settings.log_dir, "*.log")), reverse=True)
    lines = []
    if month_files:
        try:
            with open(month_files[0], "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()[-n_lines:]
        except Exception:
            pass
    return lines

def load_state():
    if not os.path.exists(STATE_PATH):
        return {}
    with open(STATE_PATH, "r") as f:
        return json.load(f)

@app.route("/")
def home():
    lines = tail_log()
    state = load_state()
    return render_template("index.html", lines=lines, state=state, refresh=settings.dashboard_refresh_sec)

@app.route("/api/health")
def api_health():
    state = load_state()
    return jsonify({
        "mode": state.get("mode", settings.mode),
        "last_run_utc": state.get("last_run_utc"),
        "caps": state.get("caps", {}),
        "positions": state.get("positions", {})
    })

@app.route("/static/<path:path>")
def static_proxy(path):
    return send_from_directory("static", path)

def run():
    app.run(host="0.0.0.0", port=settings.dashboard_port, debug=False)

if __name__ == "__main__":
    run()
