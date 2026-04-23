#!/bin/bash

DATE=$(date +"%Y-%m-%d_%H-%M")
DB_PATH="/home/pi/pvs6-monitor/backend_api/pvs6_data.db"
BACKUP_DIR="/home/pi/pvs6-monitor/backups"
BACKUP_FILE="$BACKUP_DIR/pvs6_data_$DATE.db"

# Create SQLite hot backup
sqlite3 "$DB_PATH" ".backup '$BACKUP_FILE'"

# Keep only last 30 backups
ls -1t $BACKUP_DIR/pvs6_data_*.db | tail -n +31 | xargs -r rm --

