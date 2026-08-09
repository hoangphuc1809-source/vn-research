#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo 'Install systemd service...'
sudo cp deploy/vn-research.service /etc/systemd/system/vn-research.service
sudo systemctl daemon-reload
sudo systemctl enable --now vn-research.service
sudo systemctl status vn-research.service

echo 'Build frontend...'
cd frontend
npm run build
cd ..

echo 'Create Cloudflare named tunnel...'
cloudflared tunnel create vn-research
cloudflared tunnel route dns vn-research vn-research.hoangphuc1809.workers.dev
cloudflared tunnel run vn-research &
sleep 3

echo 'URL: https://vn-research.hoangphuc1809.workers.dev'
echo 'Dashboard: https://vn-research.hoangphuc1809.workers.dev/dashboard'
