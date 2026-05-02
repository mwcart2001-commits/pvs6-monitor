#!/bin/bash
#
# pvs6-monitor Nightly Backup Script
# ----------------------------------
# Responsibilities:
#  - Create a consistent SQLite backup using `.backup`
#  - Compress the backup to .sqlite.gz
#  - Log success/failure
#  - Prepare for integrity checking + retention
#

set -euo pipefail

# === CONFIGURATION ============================================================
DB_PATH="/home/pi/pvs6-monitor/pvs6_data.db"
BACKUP_DIR="/home/pi/pvs6-monitor/backups"
LOG_DIR="/home/pi/pvs6-monitor/logs/backup"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="${BACKUP_DIR}/pvs6-${TIMESTAMP}.sqlite"
COMPRESSED_FILE="${BACKUP_FILE}.gz"

mkdir -p "$BACKUP_DIR"
mkdir -p "$LOG_DIR"

LOG_FILE="${LOG_DIR}/backup-${TIMESTAMP}.log"

# === LOGGING UTILITIES ========================================================
log() {
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1" | tee -a "$LOG_FILE"
}

# === BACKUP PROCESS ===========================================================
log "Starting nightly backup job"

if [ ! -f "$DB_PATH" ]; then
    log "ERROR: Database not found at $DB_PATH"
    exit 1
fi

log "Creating SQLite backup..."
sqlite3 "$DB_PATH" ".backup '${BACKUP_FILE}'"
log "Backup created: ${BACKUP_FILE}"

log "Compressing backup..."
gzip "$BACKUP_FILE"
log "Compressed to: ${COMPRESSED_FILE}"

log "Backup job completed successfully"
exit 0
