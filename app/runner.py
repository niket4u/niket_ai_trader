import threading, sys, traceback

def start_bot_thread():
    candidates = [("app.bot","main_loop"), ("app.bot","main"), ("app.bot","run")]
    for mod_name, func_name in candidates:
        try:
            mod = __import__(mod_name, fromlist=[func_name])
            fn = getattr(mod, func_name)
            t = threading.Thread(target=fn, daemon=True)
            t.start()
            sys.stderr.write("[i] started %s.%s in background\n" % (mod_name, func_name))
            return t
        except Exception as e:
            sys.stderr.write("[i] %s.%s not available: %s\n" % (mod_name, func_name, e))
            traceback.print_exc()
    sys.stderr.write("[i] no known bot entrypoint found; continuing with dashboard only\n")
    return None

def start_dashboard():
    try:
        from app.dashboard import run as dash_run
        dash_run(); return
    except Exception as e:
        sys.stderr.write("[i] app.dashboard.run not available: %s\n" % e)
        traceback.print_exc()
    from app.dashboard_runshim import run as shim_run
    shim_run()

if __name__ == "__main__":
    _t = start_bot_thread()
    start_dashboard()
