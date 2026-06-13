#!/bin/bash
set -e
if [ "$SERVICE" = "api" ]; then
    exec uvicorn src.api.rest:app --host 0.0.0.0 --port 8000
elif [ "$SERVICE" = "bot" ]; then
    exec python -m src.interfaces.telegram.bot
else
    echo "SERVICE must be 'api' or 'bot'"
    exit 1
fi
