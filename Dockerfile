FROM python:3.12-slim

WORKDIR /app

# نصب پیش‌نیازهای سیستمی
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# مطمئن شو اسکریپت قابل اجراست
RUN chmod +x scripts/entrypoint.sh

ENTRYPOINT ["bash", "scripts/entrypoint.sh"]
