#!/bin/bash
if [ -z "$1" ]; then
  echo "Usage: ./restore.sh <backup_file>"
  exit 1
fi
echo "Restoring from $1..."
# دانلود از S3 اگر لازم باشد
# aws s3 cp s3://$S3_BUCKET/backups/$1 /tmp/restore.sql
psql $DATABASE_SYNC_URL < /tmp/restore.sql
echo "Restore completed."
