
#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"
REPO_DIR="$(cd .. && pwd)"
cd "$REPO_DIR"

# Create venv if missing
if [[ ! -d ".venv" ]]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Keep .env local on Pi; create if missing
if [[ ! -f ".env" ]]; then
  cp .env.example .env
  echo "[i] Created .env from template. Edit it with your credentials."
fi

# Restart service if running
if systemctl is-active --quiet niketbot; then
  sudo systemctl restart niketbot
fi

echo "[+] Install/update complete."
