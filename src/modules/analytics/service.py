from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Dict, Any
from src.modules.analytics.models import EventLog
from src.core.events import Event, event_bus
import logging

logger = logging.getLogger(__name__)

class AnalyticsService:
    async def track_event(self, db: AsyncSession, event_name: str, user_id: int = None, 
                          telegram_id: int = None, properties: dict = None):
        log = EventLog(
            event_name=event_name,
            user_id=user_id,
            telegram_id=telegram_id,
            properties=properties
        )
        db.add(log)
        await db.commit()
        logger.info(f"Analytics event: {event_name}")

    async def get_event_count(self, db: AsyncSession, event_name: str, 
                              since: datetime = None) -> int:
        stmt = select(func.count()).select_from(EventLog).where(EventLog.event_name == event_name)
        if since:
            stmt = stmt.where(EventLog.created_at >= since)
        result = await db.execute(stmt)
        return result.scalar() or 0

    async def get_daily_active_users(self, db: AsyncSession, days: int = 30) -> Dict[str, Any]:
        # کوئری تعداد کاربران یکتا در هر روز
        # برای سادگی از PostgreSQL date_trunc استفاده می‌کنیم
        from datetime import datetime as dt, timedelta
        result = {}
        for i in range(days):
            day = dt.utcnow() - timedelta(days=i)
            stmt = select(func.count(func.distinct(EventLog.telegram_id))).where(
                func.date(EventLog.created_at) == day.date(),
                EventLog.event_name == "user.interaction"
            )
            res = await db.execute(stmt)
            count = res.scalar()
            result[day.date().isoformat()] = count
        return result

analytics_service = AnalyticsService()

# اتصال به رویدادها برای ضبط خودکار
async def on_event(event: Event):
    # برای ضبط رویدادها نیاز به یک session داریم که در زمان اجرا تزریق می‌شود
    # اینجا صرفاً یک placeholder
    pass
