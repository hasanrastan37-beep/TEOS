from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.modules.analytics.models import EventLog
from typing import Dict, List

class FunnelAnalyzer:
    async def purchase_funnel(self, db: AsyncSession) -> Dict[str, int]:
        steps = {
            "visited_bot": 0,
            "viewed_plans": 0,
            "initiated_purchase": 0,
            "completed_purchase": 0,
        }
        total_users = await db.execute(select(func.count(func.distinct(EventLog.telegram_id))).where(EventLog.event_name == "user.start"))
        steps["visited_bot"] = total_users.scalar() or 0
        viewed = await db.execute(select(func.count(func.distinct(EventLog.telegram_id))).where(EventLog.event_name == "service.plans_viewed"))
        steps["viewed_plans"] = viewed.scalar() or 0
        initiated = await db.execute(select(func.count(func.distinct(EventLog.telegram_id))).where(EventLog.event_name == "purchase.initiated"))
        steps["initiated_purchase"] = initiated.scalar() or 0
        completed = await db.execute(select(func.count(func.distinct(EventLog.telegram_id))).where(EventLog.event_name == "purchase.completed"))
        steps["completed_purchase"] = completed.scalar() or 0
        return steps
