# راهنمای مشارکت در TEOS

## ساختار کد
- `src/core`: هسته (تنظیمات، امنیت، event bus، موتورها)
- `src/modules`: ماژول‌های کسب‌وکار (هر پوشه یک ماژول با models, service)
- `src/interfaces/telegram`: ربات تلگرام
- `src/interfaces/web`: پنل Next.js
- `src/api`: REST/GraphQL endpoints
- `plugins`: پلاگین‌های خارجی

## افزودن ماژول جدید
1. پوشه‌ای در `src/modules/your_module` ایجاد کنید.
2. `models.py` با تعریف جداول.
3. `service.py` با منطق تجاری.
4. در صورت نیاز handlers تلگرام و endpoints API.
5. migration ایجاد کنید.

## تست‌ها
- `pytest` استفاده می‌شود.
- برای تست async از `pytest-asyncio` استفاده کنید.
