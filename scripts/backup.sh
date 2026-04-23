#!/bin/bash
timestamp=$(date +"%Y-%m-%d_%H-%M-%S")

# Stop collector briefly
sudo systemctl stop pvs6-collector.service

# Perform backup safely
sqlite3 /home/pi/pvs6-monitor/pvs6_data.db \
"VACUUM INTO '/home/pi/pvs6-monitor/backups/pvs6-$timestamp.sqlite';"

# Restart collector
sudo systemctl start pvs6-collector.service
