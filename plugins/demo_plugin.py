from src.core.plugins import PluginInterface
import logging

logger = logging.getLogger(__name__)

class DemoPlugin(PluginInterface):
    name = "demo_plugin"
    version = "1.0.0"
    
    async def on_enable(self, context):
        logger.info("Demo plugin enabled")
        # دسترسی به event bus
        eb = context.get("event_bus")
        if eb:
            async def demo_handler(event):
                logger.info(f"Demo handled event: {event.name}")
            eb.subscribe("lead.created", demo_handler)
    
    async def on_disable(self):
        logger.info("Demo plugin disabled")
