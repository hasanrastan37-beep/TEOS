# استقرار در Railway

1. پروژه را در GitHub آپلود کنید.
2. در Railway، New Project > Deploy from GitHub repo.
3. متغیرهای محیطی زیر را تنظیم کنید:
   - `DATABASE_URL` (یا از سرویس Postgres داخلی Railway استفاده کنید)
   - `REDIS_URL`
   - `SECRET_KEY`
   - `TELEGRAM_BOT_TOKEN`
4. Railway فایل `railway.json` را شناسایی کرده و سرویس‌های `teos-api`، `teos-bot` و `teos-web` را ایجاد می‌کند.
5. در صورت نیاز به دامنه سفارشی، از بخش Settings دامنه را تنظیم کنید.
6. برای webhook تلگرام، آدرس `https://your-domain.railway.app/webhook` را در `TELEGRAM_WEBHOOK_URL` قرار دهید.
