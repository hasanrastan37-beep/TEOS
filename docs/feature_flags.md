# Feature Flags در TEOS

Feature flags امکان فعال/غیرفعال کردن ویژگی‌ها را بدون تغییر کد فراهم می‌کنند.
تنظیمات از دیتابیس خوانده می‌شود و مالک می‌تواند از پنل آن را مدیریت کند.

## استفاده در کد
```python
from src.core.feature_flags import is_enabled

if await is_enabled("music_module"):
    # فعال
else:
    # غیرفعال
