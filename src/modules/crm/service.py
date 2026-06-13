from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from typing import List, Optional
from src.modules.crm.models import Lead, LeadStatus, Note
from src.core.user_engine import User
from src.core.events import event_bus, Event

class CRMService:
    async def create_lead(self, db: AsyncSession, telegram_id: Optional[int], first_name: str, 
                          last_name: Optional[str] = None, phone: Optional[str] = None, 
                          email: Optional[str] = None, source: Optional[str] = None) -> Lead:
        lead = Lead(
            telegram_id=telegram_id,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            email=email,
            source=source,
            status=LeadStatus.NEW
        )
        db.add(lead)
        await db.commit()
        await db.refresh(lead)
        await event_bus.publish(Event(name="lead.created", payload={"lead_id": lead.id}))
        return lead

    async def update_status(self, db: AsyncSession, lead_id: int, new_status: LeadStatus, admin_id: int) -> Lead:
        lead = await db.get(Lead, lead_id)
        if lead:
            lead.status = new_status
            lead.assigned_to = admin_id
            lead.last_contacted = func.now()
            await db.commit()
            await event_bus.publish(Event(name="lead.status_changed", payload={"lead_id": lead_id, "status": new_status.value}))
        return lead

    async def add_note(self, db: AsyncSession, lead_id: int, content: str, user_id: int) -> Note:
        note = Note(lead_id=lead_id, content=content, created_by=user_id)
        db.add(note)
        await db.commit()
        await db.refresh(note)
        return note

    async def list_leads(self, db: AsyncSession, status: Optional[LeadStatus] = None, 
                         assigned_to: Optional[int] = None, page: int = 1, page_size: int = 20) -> List[Lead]:
        stmt = select(Lead)
        if status:
            stmt = stmt.where(Lead.status == status)
        if assigned_to is not None:
            stmt = stmt.where(Lead.assigned_to == assigned_to)
        stmt = stmt.order_by(Lead.created_at.desc()).offset((page-1)*page_size).limit(page_size)
        result = await db.execute(stmt)
        return result.scalars().all()

crm_service = CRMService()
