from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_
from typing import List, Optional
from src.modules.crm.models import Lead, LeadStatus, Note
from src.modules.crm.advanced_models import Deal, DealStage, Activity, ActivityType, Contact
from src.modules.crm.scoring_service import scoring_service
from src.core.events import event_bus, Event
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class AdvancedCRMService:
    async def create_deal(self, db: AsyncSession, lead_id: int, name: str, amount: float = 0.0,
                         assigned_to: Optional[int] = None, expected_close: Optional[datetime] = None) -> Deal:
        deal = Deal(
            lead_id=lead_id,
            name=name,
            amount=amount,
            assigned_to=assigned_to,
            expected_close_date=expected_close
        )
        db.add(deal)
        await db.commit()
        await db.refresh(deal)
        await event_bus.publish(Event(name="deal.created", payload={"deal_id": deal.id, "lead_id": lead_id}))
        return deal

    async def update_deal_stage(self, db: AsyncSession, deal_id: int, new_stage: DealStage) -> Deal:
        deal = await db.get(Deal, deal_id)
        if deal:
            deal.stage = new_stage
            if new_stage == DealStage.CLOSED_WON:
                # به‌روزرسانی امتیاز لید
                lead = await db.get(Lead, deal.lead_id)
                if lead:
                    await scoring_service.calculate_score(db, lead)
            await db.commit()
        return deal

    async def schedule_activity(self, db: AsyncSession, deal_id: int, activity_type: ActivityType,
                               subject: str, due_date: datetime, created_by: int,
                               description: Optional[str] = None) -> Activity:
        activity = Activity(
            deal_id=deal_id,
            type=activity_type,
            subject=subject,
            description=description,
            due_date=due_date,
            created_by=created_by
        )
        db.add(activity)
        await db.commit()
        return activity

    async def get_upcoming_activities(self, db: AsyncSession, user_id: int,
                                     days_ahead: int = 7) -> List[Activity]:
        now = datetime.utcnow()
        end = now + timedelta(days=days_ahead)
        stmt = select(Activity).where(
            Activity.completed == False,
            Activity.due_date.between(now, end),
            Activity.created_by == user_id
        ).order_by(Activity.due_date)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_pipeline_summary(self, db: AsyncSession) -> dict:
        stmt = select(
            Deal.stage,
            func.count(Deal.id).label("count"),
            func.sum(Deal.amount).label("total_value")
        ).group_by(Deal.stage)
        result = await db.execute(stmt)
        rows = result.all()
        summary = {}
        for stage, count, total in rows:
            summary[stage.value] = {"count": count, "total_value": float(total or 0)}
        return summary

    async def add_contact(self, db: AsyncSession, lead_id: int, name: str,
                         email: Optional[str] = None, phone: Optional[str] = None,
                         position: Optional[str] = None, is_primary: bool = False) -> Contact:
        if is_primary:
            # بقیه را غیر اصلی کن
            await db.execute(update(Contact).where(Contact.lead_id == lead_id).values(is_primary=False))
        contact = Contact(lead_id=lead_id, name=name, email=email, phone=phone,
                         position=position, is_primary=is_primary)
        db.add(contact)
        await db.commit()
        return contact

crm_advanced_service = AdvancedCRMService()
