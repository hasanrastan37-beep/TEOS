from sqlalchemy import String, Integer, Boolean, DateTime, Text, ForeignKey, Float, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base, TimestampMixin
from typing import Optional, List
import enum
import datetime

class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL_SENT = "proposal_sent"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"

class Lead(Base, TimestampMixin):
    __tablename__ = "crm_leads"
    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[Optional[int]] = mapped_column(index=True)
    first_name: Mapped[str] = mapped_column(String(128))
    last_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    status: Mapped[LeadStatus] = mapped_column(default=LeadStatus.NEW)
    source: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)  # referral, search, ad...
    assigned_to: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)  # ادمین مسئول
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_contacted: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    # روابط
    assigned_user = relationship("User", foreign_keys=[assigned_to])

class Note(Base):
    __tablename__ = "crm_notes"
    id: Mapped[int] = mapped_column(primary_key=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("crm_leads.id"))
    content: Mapped[str] = mapped_column(Text)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    lead = relationship("Lead", back_populates="notes_list")
    creator = relationship("User")
