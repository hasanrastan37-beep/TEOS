# معماری TEOS

TEOS یک سیستم چهار لایه است:

1. **Infrastructure Layer**: Kubernetes/Docker, PostgreSQL, Redis, Elasticsearch, S3
2. **Core Engine**: User, Role, Permission, Event, Workflow, Plugin, AI, Rule, Automation
3. **Business Modules**: Music, Service/VPN, Wallet, Ticket, CRM, Analytics, Marketing, Referral
4. **Interface Layer**: Telegram Bot, Web Admin Panel (Next.js), REST API, GraphQL, Future Mobile

هر لایه کاملاً مستقل و از طریق واسط‌های مشخص با یکدیگر ارتباط برقرار می‌کنند.
تمامی تنظیمات در دیتابیس ذخیره شده و از طریق پنل No-Code قابل تغییر هستند.
