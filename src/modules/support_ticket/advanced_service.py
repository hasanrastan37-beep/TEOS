from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from src.modules.support_ticket.models import Ticket, TicketMessage, TicketStatus
from src.modules.support_ticket.sla_models import SLAPolicy, SLATracking
from src.core.events import event_bus, Event
import logging

logger = logging.getLogger(__name__)

class AdvancedTicketService:
    async def auto_assign(self, db: AsyncSession, ticket: Ticket):
        # پیدا کردن ادمین با کمترین تیکت باز
        from src.core.user_engine import User
        stmt = select(User).where(User.role.in_(["admin_music", "admin_vpn", "owner"]), User.is_blocked == False)
        admins = (await db.execute(stmt)).scalars().all()
        if not admins:
            return
        # شمارش تیکت‌های باز هر ادمین
        admin_counts = {}
        for admin in admins:
            count_stmt = select(Ticket).where(Ticket.assigned_admin_id == admin.id, Ticket.status != TicketStatus.CLOSED)
            count = (await db.execute(count_stmt)).scalars().all()
            admin_counts[admin.id] = len(count)
        assigned = min(admins, key=lambda a: admin_counts.get(a.id, 0))
        ticket.assigned_admin_id = assigned.id
        await db.commit()
        logger.info(f"Ticket {ticket.id} auto-assigned to admin {assigned.id}")

    async def check_sla(self, db: AsyncSession, ticket_id: int):
        ticket = await db.get(Ticket, ticket_id)
        if not ticket:
            return
        sla_policy = await db.execute(select(SLAPolicy).where(SLAPolicy.priority == ticket.priority.value))
        policy = sla_policy.scalars().first()
        if not policy:
            return
        tracking = await db.get(SLATracking, ticket_id)
        if not tracking:
            tracking = SLATracking(ticket_id=ticket.id)
            db.add(tracking)
            await db.commit()
        now = datetime.now(timezone.utc)
        # بررسی زمان پاسخ
        if ticket.created_at and not tracking.responded_at:
            if (now - ticket.created_at).total_seconds() / 60 > policy.response_time_minutes:
                if not tracking.breached:
                    tracking.breached = True
                    await db.commit()
                    await event_bus.publish(Event(name="sla.breach.response", payload={"ticket_id": ticket.id}))
        # بررسی زمان حل
        if ticket.created_at and not tracking.resolved_at and ticket.status != TicketStatus.CLOSED:
            if (now - ticket.created_at).total_seconds() / 60 > policy.resolution_time_minutes:
                if not tracking.breached:
                    tracking.breached = True
                    await db.commit()
                    await event_bus.publish(Event(name="sla.breach.resolution", payload={"ticket_id": ticket.id}))

advanced_ticket_service = AdvancedTicketService()
