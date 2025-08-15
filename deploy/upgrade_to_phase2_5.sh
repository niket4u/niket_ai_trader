#!/usr/bin/env bash
# upgrade_to_phase_2_5.sh — run this on the Pi
# Upgrades your local repo working copy to Phase 2.5, installs deps, restarts service.
set -euo pipefail

REPO_DIR="${HOME}/niket_ai_trader"
SERVICE_NAME="niketbot"
LOCKFILE="/tmp/niketbot_upgrade.lock"
BRANCH=""
DO_DRIVE=0
DO_HEALTH=1

# Args:
#   --branch <name>   (optional) checkout specific branch
#   --with-drive      (optional) install Drive deps and enable weekly sync timer
#   --no-health       (optional) skip health check

while [[ $# -gt 0 ]]; do
  case "$1" in
    --branch) BRANCH="${2:-}"; shift 2;;
    --with-drive) DO_DRIVE=1; shift;;
    --no-health) DO_HEALTH=0; shift;;
    *) echo "Unknown arg: $1"; exit 2;;
  esac
done

# Lock
exec 9>"$LOCKFILE"
if ! flock -n 9; then
  echo "[!] Another upgrade is running. Exiting."
  exit 0
fi

# Repo exists?
if [[ ! -d "$REPO_DIR" ]]; then
  echo "[!] Repo not found at $REPO_DIR"
  echo "    Clone first: git clone https://github.com/niket4u/niket_ai_trader \"$REPO_DIR\""
  exit 1
fi

cd "$REPO_DIR"
echo "[i] Repo: $REPO_DIR"

# Stop service if present
if systemctl list-units --type=service --all | grep -q "${SERVICE_NAME}\.service"; then
  echo "[i] Stopping ${SERVICE_NAME}..."
  sudo systemctl stop "${SERVICE_NAME}" || true
fi

# Backup .env
if [[ -f ".env" ]]; then
  TS="$(date +%Y%m%d_%H%M%S)"
  cp .env "${HOME}/niket_ai_trader.env.backup.${TS}"
  echo "[i] Backed up .env to ${HOME}/niket_ai_trader.env.backup.${TS}"
fi

# Connectivity
echo "[i] Checking connectivity to github.com:443 ..."
if ! timeout 5 bash -c "cat < /dev/null > /dev/tcp/github.com/443" 2>/dev/null; then
  echo "[!] No connectivity to github.com:443. Try again later."
  exit 1
fi

# Fetch / checkout / pull
echo "[i] Fetching latest..."
git fetch origin
if [[ -n "$BRANCH" ]]; then
  echo "[i] Checking out branch: $BRANCH"
  git checkout "$BRANCH"
fi
UPSTREAM="$(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || true)"
if [[ -z "$UPSTREAM" ]]; then
  CURBR="$(git rev-parse --abbrev-ref HEAD)"
  echo "[i] Setting upstream to origin/${CURBR}"
  git branch --set-upstream-to "origin/${CURBR}" || true
fi
echo "[i] Pulling with rebase/autostash ..."
git pull --rebase --autostash

# Install/update deps + (re)start if already installed
echo "[i] Running deploy/install_or_update.sh ..."
bash deploy/install_or_update.sh

# Enable daily autoupdate timer
if [[ -f "deploy/autoupdate.service" && -f "deploy/autoupdate.timer" ]]; then
  echo "[i] Enabling daily autoupdate timer ..."
  sudo cp deploy/autoupdate.service /etc/systemd/system/
  sudo cp deploy/autoupdate.timer /etc/systemd/system/
  sudo systemctl daemon-reload
  sudo systemctl enable autoupdate.timer
  sudo systemctl start autoupdate.timer
fi

# Optional: Google Drive weekly sync
if [[ "$DO_DRIVE" -eq 1 ]]; then
  if [[ -f "requirements_drive.txt" ]]; then
    echo "[i] Installing Google Drive dependencies ..."
    source .venv/bin/activate
    pip install -r requirements_drive.txt
  fi
  if [[ -f "deploy/install_drive_sync.sh" ]]; then
    echo "[i] Enabling weekly Drive sync timer ..."
    bash deploy/install_drive_sync.sh
  else
    echo "[i] Drive sync installer not found; skipping."
  fi
fi

# Enable & start app service
if [[ -f "deploy/niketbot.service" ]]; then
  echo "[i] Installing ${SERVICE_NAME}.service ..."
  sudo cp deploy/niketbot.service /etc/systemd/system/
  sudo systemctl daemon-reload
  sudo systemctl enable "${SERVICE_NAME}"
  sudo systemctl restart "${SERVICE_NAME}"
else
  echo "[!] Missing deploy/niketbot.service; cannot start service automatically."
fi

# Version stamp (optional)
if [[ -w /etc ]]; then
  echo "phase-2.5" | sudo tee /etc/niketbot_version >/dev/null || true
fi

# Health check
if [[ "$DO_HEALTH" -eq 1 ]]; then
  HEALTH_URL="http://localhost:8080/api/health"
  echo "[i] Health check: $HEALTH_URL"
  if command -v curl >/dev/null 2>&1; then
    sleep 2
    if curl -fsS --max-time 5 "$HEALTH_URL" >/dev/null; then
      echo "[+] Health OK."
    else
      echo "[!] Health check failed. See logs: journalctl -u ${SERVICE_NAME} -n 200 --no-pager"
    fi
  else
    echo "[i] curl not installed; skipping health check."
  fi
fi

echo ""
echo "[✓] Upgrade to Phase 2.5 complete."
echo "    Status:   systemctl status ${SERVICE_NAME} --no-pager"
echo "    Logs:     journalctl -u ${SERVICE_NAME} -n 100 --no-pager"
echo "    Health:   curl http://localhost:8080/api/health"
echo ""
