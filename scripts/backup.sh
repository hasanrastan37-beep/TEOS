#!/bin/bash
# اسکریپت پشتیبان‌گیری دیتابیس
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="/backups/teos_backup_$TIMESTAMP.sql"
pg_dump -U teos -h localhost teos > $BACKUP_FILE
echo "Backup saved to $BACKUP_FILE"
# آپلود به S3 اگر تنظیم شده باشد
if [ -n "$S3_BUCKET" ]; then
  aws s3 cp $BACKUP_FILE s3://$S3_BUCKET/backups/
fi
