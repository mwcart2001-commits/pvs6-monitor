#!/bin/bash
#
# pvs6-monitor Backup Retention Script
# ------------------------------------
# Deletes old compressed backups older than N days.
# Logs all deletions and errors.
#

set -euo pipefail

# === CONFIGURATION ============================================================
BACKUP_DIR="/home/pi/pvs6-monitor/backups"
LOG_DIR="/home/pi/pvs6-monitor/logs/backup"
RETENTION_DAYS=14   # <-- Adjust as needed

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_FILE="${LOG_DIR}/retention-${TIMESTAMP}.log"

mkdir -p "$LOG_DIR"

# === LOGGING UTILITIES ========================================================
log() {
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1" | tee -a "$LOG_FILE"
}

# === RETENTION PROCESS ========================================================
log "Starting backup retention cleanup (older than ${RETENTION_DAYS} days)"

if [ ! -d "$BACKUP_DIR" ]; then
    log "ERROR: Backup directory not found: $BACKUP_DIR"
    exit 1
fi

# Find and delete old backups
OLD_FILES=$(find "$BACKUP_DIR" -type f -name "*.sqlite.gz" -mtime +$RETENTION_DAYS)

if [ -z "$OLD_FILES" ]; then
    log "No backups older than ${RETENTION_DAYS} days found"
    log "Retention cleanup completed"
    exit 0
fi

log "Deleting the following old backups:"
echo "$OLD_FILES" | tee -a "$LOG_FILE"

# Delete them
echo "$OLD_FILES" | xargs rm -f

log "Retention cleanup completed successfully"
exit 0
