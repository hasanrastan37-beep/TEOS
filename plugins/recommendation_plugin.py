from src.core.plugins import PluginInterface
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import async_session
from src.modules.music.models import Track
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

class RecommendationPlugin(PluginInterface):
    name = "recommendation_engine"
    version = "1.2.0"

    async def on_enable(self, context):
        logger.info("Recommendation plugin enabled")
        # ثبت یک event handler
        event_bus = context.get("event_bus")
        if event_bus:
            event_bus.subscribe("user.interaction", self.handle_interaction)

    async def handle_interaction(self, event):
        # ذخیره تعامل و بازآموزی دوره‌ای
        pass

    async def get_recommendations(self, user_id: int, top_n: int = 5):
        # بارگذاری ماتریس رتبه‌بندی‌ها
        # ساده‌سازی: بازگرداندن آهنگ‌های با بالاترین لایک
        async with async_session() as db:
            tracks = await db.execute(select(Track).order_by(Track.likes.desc()).limit(top_n))
            return tracks.scalars().all()
