# Telegram Enterprise Operating System (TEOS)

TEOS یک پلتفرم سازمانی هوشمند، چندمستاجره، AI‑محور و Plugin‑محور است که از Telegram به عنوان یکی از رابط‌های خود استفاده می‌کند.
این سیستم بر پایه معماری چندلایه (Infrastructure, Core Engine, Business Modules, Interface Layer) طراحی شده و کاملاً از طریق پنل مدیریتی No‑Code قابل تنظیم است.

## ویژگی‌های کلیدی
- هستهٔ ماژولار و رویدادمحور
- موتور AI با قابلیت ساخت Agentهای جدید از پنل
- Rule Engine بصری بدون نیاز به کدنویسی
- Workflow Builder برای طراحی فرآیندهای سازمانی
- Dynamic Entity System (تعریف موجودیت‌های جدید از پنل)
- Plugin Operating System با پشتیبانی از نصب/حذف/به‌روزرسانی بدون توقف
- Multi‑Tenant با پنل‌های مستقل
- رابط Telegram، API REST، GraphQL و پنل تحت وب (Next.js)
- امنیت پیشرفته، لاگ ساخت‌یافته، مانیتورینگ کامل

## شروع سریع
1. کپی فایل `.env.example` به `.env` و تنظیم متغیرها
2. اجرا با Docker Compose:
   ```bash
   docker compose up -d
