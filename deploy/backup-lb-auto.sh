#!/usr/bin/env bash
set -euo pipefail

app_dir="${LB_AUTO_APP_DIR:-/opt/lb-auto}"
backup_dir="${LB_AUTO_BACKUP_DIR:-/var/backups/lb-auto}"
timestamp="$(date +%Y%m%d-%H%M%S)"

test -f "${app_dir}/lb_auto.db"
test -d "${app_dir}/uploads"
test -d "${backup_dir}"

sqlite3 "${app_dir}/lb_auto.db" ".backup '${backup_dir}/lb_auto-${timestamp}.db'"
tar -C "${app_dir}" -czf "${backup_dir}/uploads-${timestamp}.tar.gz" uploads

# Retain the most recent 30 days of automatic backups.
find "${backup_dir}" -maxdepth 1 -type f \( -name 'lb_auto-*.db' -o -name 'uploads-*.tar.gz' \) -mtime +30 -delete
