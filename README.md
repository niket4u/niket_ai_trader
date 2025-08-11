
# Niket AI Trader — Phase 2 (Test Build)

This build adds:
- **Cloudflare Tunnel** exposing the Flask dashboard securely over HTTPS (no port-forwarding).
- **Git-based deployment & autoupdate** (daily + on-boot) with systemd.
- **Minimal SD usage**: logs go to tmpfs (`/tmp/niketbot_logs`) with retention.
- **Dashboard improvements**: health JSON, state snapshot, basic status cards.
- **Daily summary email** (optional) after U.S. market close.

> Your `.env` lives on the Pi and is **not** tracked by git.

---

## One-time setup on Raspberry Pi

```bash
# 0) install git & clone (or your own GitHub repo once you push this there)
sudo apt-get update -y && sudo apt-get install -y git python3-venv python3-pip
cd ~
git clone <your-repo-url> niket_ai_trader
cd ~/niket_ai_trader
# first install
bash deploy/install_or_update.sh
```

### Configure Cloudflare Tunnel (once)
```bash
# Install cloudflared & log in
bash deploy/install_cloudflared.sh
cloudflared tunnel login
# Create a tunnel (follow prompts) and note the TUNNEL_NAME
cloudflared tunnel create niketbot
# Set your hostname (replace with your subdomain)
export CF_HOSTNAME=niketbot.yourdomain.com
bash deploy/setup_cloudflared.sh niketbot $CF_HOSTNAME
# Enable & start cloudflared at boot
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
```

### Enable the app service + autoupdate
```bash
# App on boot
sudo cp deploy/niketbot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable niketbot
sudo systemctl start niketbot

# Daily autoupdate (pull & restart if needed)
sudo cp deploy/autoupdate.service /etc/systemd/system/
sudo cp deploy/autoupdate.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable autoupdate.timer
sudo systemctl start autoupdate.timer
```

---

## Updating later
Push commits to your git remote, then either wait for the timer, or run:
```bash
cd ~/niket_ai_trader
bash deploy/install_or_update.sh
```

---

## Environment
Copy `.env.example` to `.env` on the Pi and edit values (Gmail App Password, caps, etc.).

---

## Minimal SD Usage
- Logs live in `/tmp/niketbot_logs` (tmpfs). Retention is controlled by `LOG_RETENTION_DAYS`.
- If you want persistent logs, set `LOG_DIR` in `.env` to somewhere on an external drive (recommended) or to `logs/` (SD), and consider logrotate.

---

## Security
- Dashboard can be optionally protected with basic auth (`DASHBOARD_USER`, `DASHBOARD_PASS`).
- Cloudflare Tunnel terminates TLS and routes to `http://localhost:8080` on the Pi.

---

## Notes
- Phase 2 still **does not execute live trades**. Alerts only.
- Daily summary email runs shortly after the U.S. market close.
