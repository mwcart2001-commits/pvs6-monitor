#!/bin/bash

echo "Stopping Vite dev server..."
sudo systemctl stop pvs6-dashboard-dev

echo "Building production dashboard..."
cd /home/pi/pvs6-monitor/solar-dashboard
npm run build

echo "Switching Caddy to production mode..."
sudo cp /home/pi/pvs6-monitor/Caddyfile.prod /etc/caddy/Caddyfile

echo "Restarting Caddy..."
sudo systemctl restart caddy

echo "Production mode activated."
sudo systemctl status caddy --no-pager

echo "prod" > ~/pvs6-monitor/mode
