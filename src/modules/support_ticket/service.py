from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from src.modules.support_ticket.models import Ticket, TicketMessage, TicketStatus, TicketPriority
from src.core.events import event_bus, Event

class TicketService:
    async def create_ticket(self, db: AsyncSession, user_id: int, subject: str, initial_message: str,
                            priority: TicketPriority = TicketPriority.MEDIUM) -> Ticket:
        ticket = Ticket(user_id=user_id, subject=subject, priority=priority)
        db.add(ticket)
        await db.flush()
        msg = TicketMessage(ticket_id=ticket.id, sender_id=user_id, content=initial_message)
        db.add(msg)
        await db.commit()
        await db.refresh(ticket)
        await event_bus.publish(Event(name="ticket.created", payload={"ticket_id": ticket.id, "user_id": user_id}))
        return ticket

    async def reply_to_ticket(self, db: AsyncSession, ticket_id: int, sender_id: int, content: str,
                              is_admin: bool = False, file_id: str = None) -> TicketMessage:
        ticket = await db.get(Ticket, ticket_id)
        if not ticket or ticket.status == TicketStatus.CLOSED:
            raise ValueError("Ticket not found or closed")
        msg = TicketMessage(ticket_id=ticket_id, sender_id=sender_id, content=content,
                            is_admin_reply=is_admin, file_id=file_id)
        db.add(msg)
        if is_admin:
            ticket.status = TicketStatus.WAITING_USER
        else:
            ticket.status = TicketStatus.IN_PROGRESS
        await db.commit()
        return msg

    async def assign_ticket(self, db: AsyncSession, ticket_id: int, admin_id: int):
        ticket = await db.get(Ticket, ticket_id)
        if ticket:
            ticket.assigned_admin_id = admin_id
            ticket.status = TicketStatus.IN_PROGRESS
            await db.commit()

    async def close_ticket(self, db: AsyncSession, ticket_id: int):
        ticket = await db.get(Ticket, ticket_id)
        if ticket:
            ticket.status = TicketStatus.CLOSED
            ticket.closed_at = func.now()
            await db.commit()

ticket_service = TicketService()
