import importlib
import importlib.util
import sys
import os
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class PluginInterface:
    """رابطی که هر پلاگین باید پیاده‌سازی کند."""
    name: str = ""
    version: str = "0.1.0"
    
    async def on_enable(self, context: Dict[str, Any]):
        pass

    async def on_disable(self):
        pass

    async def on_install(self):
        pass

    async def on_uninstall(self):
        pass

class PluginManager:
    def __init__(self, plugin_dir: str = "./plugins"):
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, Any] = {}

    def discover(self):
        sys.path.insert(0, self.plugin_dir)
        for item in os.listdir(self.plugin_dir):
            if item.endswith(".py") and not item.startswith("__"):
                module_name = item[:-3]
                spec = importlib.util.spec_from_file_location(module_name, os.path.join(self.plugin_dir, item))
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type) and issubclass(attr, PluginInterface) and attr != PluginInterface:
                            plugin_instance = attr()
                            self.plugins[plugin_instance.name] = plugin_instance
                            logger.info(f"Discovered plugin: {plugin_instance.name} v{plugin_instance.version}")

    async def enable_plugin(self, name: str):
        plugin = self.plugins.get(name)
        if plugin:
            await plugin.on_enable({"manager": self})

    async def disable_plugin(self, name: str):
        plugin = self.plugins.get(name)
        if plugin:
            await plugin.on_disable()

plugin_manager = PluginManager()
