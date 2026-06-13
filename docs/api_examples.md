# TEOS API Examples

## ساخت آهنگ جدید
```bash
curl -X POST http://localhost:8000/admin/music/tracks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"title":"New Song","artist":"Artist","genre":"pop"}'
