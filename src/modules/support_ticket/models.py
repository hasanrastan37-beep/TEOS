from sqlalchemy import String, Text, DateTime, Boolean, Integer, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base, TimestampMixin
from typing import Optional, List
import enum
import datetime

class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_USER = "waiting_user"
    RESOLVED = "resolved"
    CLOSED = "closed"

class TicketPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Ticket(Base, TimestampMixin):
    __tablename__ = "support_tickets"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    subject: Mapped[str] = mapped_column(String(256))
    status: Mapped[TicketStatus] = mapped_column(default=TicketStatus.OPEN)
    priority: Mapped[TicketPriority] = mapped_column(default=TicketPriority.MEDIUM)
    assigned_admin_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    closed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    user = relationship("User", foreign_keys=[user_id])
    assigned_admin = relationship("User", foreign_keys=[assigned_admin_id])
    messages = relationship("TicketMessage", back_populates="ticket", order_by="TicketMessage.created_at")

class TicketMessage(Base, TimestampMixin):
    __tablename__ = "support_ticket_messages"
    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("support_tickets.id"))
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    content: Mapped[str] = mapped_column(Text)
    is_admin_reply: Mapped[bool] = mapped_column(default=False)
    file_id: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    ticket = relationship("Ticket", back_populates="messages")
    sender = relationship("User")
