#!/bin/bash
set -euo pipefail

timestamp=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_DIR="/home/pi/pvs6-monitor/backups"
WORK_DIR="/home/pi/pvs6-monitor/tmp_backup"
DB_SOURCE="/home/pi/pvs6-monitor/pvs6_data.db"
LOG_FILE="/home/pi/rclone-backup.log"

mkdir -p "$BACKUP_DIR" "$WORK_DIR"

echo "[$(date)] Starting backup" | tee -a "$LOG_FILE"

# 1) Stop collector briefly for a clean snapshot
sudo systemctl stop pvs6-collector.service

# 2) Create a clean SQLite backup using VACUUM INTO
SQLITE_BACKUP="$WORK_DIR/pvs6-$timestamp.sqlite"
sqlite3 "$DB_SOURCE" "VACUUM INTO '$SQLITE_BACKUP';"

# 3) Restart collector immediately
sudo systemctl start pvs6-collector.service

# 4) Integrity check
INTEGRITY=$(sqlite3 "$SQLITE_BACKUP" "PRAGMA integrity_check;")
if [ "$INTEGRITY" != "ok" ]; then
  echo "[$(date)] Integrity check FAILED: $INTEGRITY" | tee -a "$LOG_FILE"
  logger "PVS6 backup FAILED: integrity check"
  exit 1
fi
echo "[$(date)] Integrity check OK" | tee -a "$LOG_FILE"

# 5) Compress backup
GZ_BACKUP="$WORK_DIR/pvs6-$timestamp.sqlite.gz"
gzip -c "$SQLITE_BACKUP" > "$GZ_BACKUP"
rm -f "$SQLITE_BACKUP"

# 6) Move compressed file to backup directory
FINAL_LOCAL="$BACKUP_DIR/$(basename "$GZ_BACKUP")"
mv "$GZ_BACKUP" "$FINAL_LOCAL"

# 7) Upload to encrypted OneDrive remote
rclone sync "$BACKUP_DIR" onedrive-crypt: \
  --onedrive-upload-cutoff 0 \
  --onedrive-chunk-size 10M \
  --transfers 1 \
  -vv \
  --log-file "$LOG_FILE"

# 8) Log success
echo "[$(date)] Backup completed successfully: $(basename "$FINAL_LOCAL")" | tee -a "$LOG_FILE"
logger "PVS6 backup completed successfully: $(basename "$FINAL_LOCAL")"

# 9) Optional: healthcheck ping
# curl -fsS https://hc-ping.com/YOUR-UUID-HERE >/dev/null 2>&1 || true
