# TEOS API Reference

Base URL: `https://your-instance.com`

## Authentication
- `POST /auth/login` – دریافت توکن JWT.

## Admin Endpoints
- `GET /admin/users/` – لیست کاربران
- `PUT /admin/users/{id}` – ویرایش کاربر

## Music Admin
- `GET /admin/music/tracks` – لیست آهنگ‌ها
- `POST /admin/music/tracks` – افزودن آهنگ

## Owner
- `GET /owner/menus/tree` – درخت منوها
- `POST /owner/menus/node` – ایجاد گرهٔ منو

## Entity Builder
- `POST /entity-builder/definitions` – تعریف موجودیت جدید
- `POST /entity-builder/records/{name}` – افزودن رکورد

## Workflow Designer
- `POST /workflow-designer/` – ذخیره طراحی
