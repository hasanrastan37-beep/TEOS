# Plugin SDK

TEOS از معماری Plugin‑first پیروی می‌کند. هر پلاگین یک کلاس Python است که رابط `PluginInterface` را پیاده‌سازی می‌کند.

## ساختار پایه
فایل پلاگین را در پوشه `plugins/` قرار دهید.
نام فایل باید با نام پلاگین یکی باشد (به‌جز پسوند `.py`).

## مثال:
```python
from src.core.plugins import PluginInterface
class MyPlugin(PluginInterface):
    name = "my_plugin"
    version = "1.0.0"
    async def on_enable(self, context):
        print("Plugin enabled")
    async def on_disable(self):
        print("Plugin disabled")
