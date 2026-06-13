#!/bin/bash
set -e

# اجرای migration
alembic upgrade head

# شروع سرویس بر اساس متغیر
if [ "$SERVICE" = "api" ]; then
    exec uvicorn src.api.rest:app --host 0.0.0.0 --port 8000
elif [ "$SERVICE" = "bot" ]; then
    exec python -m src.interfaces.telegram.bot
else
    echo "SERVICE not set"
    exit 1
fi
