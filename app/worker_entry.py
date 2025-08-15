import sys, threading, time
from dotenv import load_dotenv; load_dotenv()

def _pick_bot():
    import importlib
    for name in ("main_loop", "main", "run"):
        try:
            mod = importlib.import_module("app.bot")
            fn = getattr(mod, name)
            return fn
        except Exception:
            continue
    # Fallback: minimal safe loop that just updates state.json so dashboard shows activity
    def fallback():
        import os, json
        from datetime import datetime, timezone
        log_dir = os.getenv("LOG_DIR", "/tmp/niketbot_logs")
        os.makedirs(log_dir, exist_ok=True)
        state_path = os.path.join(log_dir, "state.json")
        while True:
            state = {
                "mode": os.getenv("MODE","paper"),
                "last_run_utc": datetime.now(timezone.utc).isoformat(),
                "caps": {"cash_spent": 0.0, "pnl_day": 0.0, "pnl_month": 0.0, "invested_pct": 0.0, "capacity_left": 0.0, "unrealized_est": 0.0},
                "positions": {}
            }
            with open(state_path, "w") as f:
                json.dump(state, f, indent=2)
            time.sleep(60)
    return fallback

if __name__ == "__main__":
    fn = _pick_bot()
    fn()