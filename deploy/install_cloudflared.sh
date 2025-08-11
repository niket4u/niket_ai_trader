
#!/usr/bin/env bash
set -euo pipefail
if command -v cloudflared >/dev/null 2>&1; then
  echo "[i] cloudflared already installed."
  exit 0
fi
echo "[+] Installing cloudflared..."
# Official repo install
curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | sudo tee /usr/share/keyrings/cloudflare-main.gpg >/dev/null
echo "deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/ $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/cloudflared.list
sudo apt-get update -y
sudo apt-get install -y cloudflared
echo "[+] cloudflared installed."
