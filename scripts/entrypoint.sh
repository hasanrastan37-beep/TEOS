#!/bin/bash
set -e

# اجرای migration (اگر نیاز بود)
# alembic upgrade head

if [ "$SERVICE" = "api" ]; then
    exec uvicorn src.api.rest:app --host 0.0.0.0 --port 8000
elif [ "$SERVICE" = "bot" ]; then
    exec python -m src.interfaces.telegram.bot
else
    echo "SERVICE not set or invalid. Use 'api' or 'bot'"
    exit 1
fi
