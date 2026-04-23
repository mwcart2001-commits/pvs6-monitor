#!/bin/bash

echo "Switching Caddy to dev mode..."
sudo cp /home/pi/pvs6-monitor/Caddyfile.dev /etc/caddy/Caddyfile

echo "Restarting Caddy..."
sudo systemctl restart caddy

echo "Starting Vite dev server..."
sudo systemctl start pvs6-dashboard-dev

echo "Dev mode activated."
sudo systemctl status pvs6-dashboard-dev --no-pager

echo "dev" > ~/pvs6-monitor/mode
