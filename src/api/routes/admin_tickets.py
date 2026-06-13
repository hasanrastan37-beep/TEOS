from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import async_session
from src.modules.support_ticket.models import Ticket, TicketMessage, TicketStatus
from src.modules.support_ticket.service import ticket_service
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/admin/tickets", tags=["Admin Tickets"])

class TicketOut(BaseModel):
    id: int
    subject: str
    status: str
    priority: str
    created_at: str

class MessageOut(BaseModel):
    id: int
    sender_id: int
    content: str
    is_admin_reply: bool
    created_at: str

class ReplyIn(BaseModel):
    content: str

@router.get("/", response_model=List[TicketOut])
async def list_tickets(status: Optional[str] = None):
    async with async_session() as db:
        stmt = select(Ticket)
        if status:
            stmt = stmt.where(Ticket.status == status)
        stmt = stmt.order_by(Ticket.created_at.desc()).limit(50)
        result = await db.execute(stmt)
        tickets = result.scalars().all()
        return [TicketOut(id=t.id, subject=t.subject, status=t.status.value, priority=t.priority.value, created_at=t.created_at.isoformat()) for t in tickets]

@router.get("/{ticket_id}/messages", response_model=List[MessageOut])
async def get_messages(ticket_id: int):
    async with async_session() as db:
        msgs = await db.execute(select(TicketMessage).where(TicketMessage.ticket_id == ticket_id).order_by(TicketMessage.created_at))
        messages = msgs.scalars().all()
        return [MessageOut(id=m.id, sender_id=m.sender_id, content=m.content, is_admin_reply=m.is_admin_reply, created_at=m.created_at.isoformat()) for m in messages]

@router.post("/{ticket_id}/reply")
async def reply_ticket(ticket_id: int, reply: ReplyIn):
    async with async_session() as db:
        await ticket_service.reply_to_ticket(db, ticket_id, sender_id=1, content=reply.content, is_admin=True)  # admin id ساده‌سازی
        return {"message": "Reply sent"}
