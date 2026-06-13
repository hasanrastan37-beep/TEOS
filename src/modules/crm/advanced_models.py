from sqlalchemy import String, Integer, Boolean, DateTime, Text, ForeignKey, Float, Enum as SAEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base, TimestampMixin
from typing import Optional, List
import enum
import datetime

class DealStage(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"

class ActivityType(str, enum.Enum):
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"
    NOTE = "note"
    TASK = "task"

class Deal(Base, TimestampMixin):
    __tablename__ = "crm_deals"
    id: Mapped[int] = mapped_column(primary_key=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("crm_leads.id"))
    name: Mapped[str] = mapped_column(String(256))
    amount: Mapped[float] = mapped_column(Float, default=0.0)
    stage: Mapped[DealStage] = mapped_column(default=DealStage.NEW)
    expected_close_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    probability: Mapped[int] = mapped_column(Integer, default=10)  # درصد
    assigned_to: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lead = relationship("Lead", back_populates="deals")
    assigned_user = relationship("User", foreign_keys=[assigned_to])
    activities = relationship("Activity", back_populates="deal", order_by="Activity.created_at")

class Activity(Base, TimestampMixin):
    __tablename__ = "crm_activities"
    id: Mapped[int] = mapped_column(primary_key=True)
    deal_id: Mapped[int] = mapped_column(ForeignKey("crm_deals.id"))
    type: Mapped[ActivityType] = mapped_column(default=ActivityType.NOTE)
    subject: Mapped[str] = mapped_column(String(256))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    due_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    completed: Mapped[bool] = mapped_column(default=False)
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    deal = relationship("Deal", back_populates="activities")
    creator = relationship("User", foreign_keys=[created_by])

class Contact(Base):
    __tablename__ = "crm_contacts"
    id: Mapped[int] = mapped_column(primary_key=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("crm_leads.id"))
    name: Mapped[str] = mapped_column(String(128))
    position: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    is_primary: Mapped[bool] = mapped_column(default=False)
    lead = relationship("Lead", back_populates="contacts")
