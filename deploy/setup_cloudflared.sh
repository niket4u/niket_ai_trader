
#!/usr/bin/env bash
set -euo pipefail
if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <TUNNEL_NAME> <HOSTNAME>"
  exit 1
fi
TUNNEL_NAME="$1"
HOSTNAME="$2"

# Create config file mapping hostname -> localhost:8080
mkdir -p ~/.cloudflared
cat > ~/.cloudflared/config.yml <<EOF
tunnel: ${TUNNEL_NAME}
credentials-file: /home/${USER}/.cloudflared/${TUNNEL_NAME}.json
ingress:
  - hostname: ${HOSTNAME}
    service: http://localhost:8080
  - service: http_status:404
EOF

# Create systemd unit & enable
sudo cloudflared --config /home/${USER}/.cloudflared/config.yml service install
echo "[+] Cloudflared configured for ${HOSTNAME}. Start service with: sudo systemctl start cloudflared"
