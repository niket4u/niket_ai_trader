import os
from dotenv import load_dotenv; load_dotenv()

# Try your project's dashboard first
try:
    from app.dashboard import run as dash_run
except Exception:
    from app.dashboard_runshim import run as dash_run

if __name__ == "__main__":
    dash_run()