#!/usr/bin/env bash
set -euo pipefail
sudo cp deploy/drive_sync.service /etc/systemd/system/
sudo cp deploy/drive_sync.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable drive_sync.timer
sudo systemctl start drive_sync.timer
echo '[+] Drive sync timer enabled (weekly).'
