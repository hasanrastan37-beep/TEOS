from sqlalchemy import String, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from src.core.database import Base
import datetime

class SLAPolicy(Base):
    __tablename__ = "sla_policies"
    id: Mapped[int] = mapped_column(primary_key=True)
    priority: Mapped[str] = mapped_column(String(16))  # low, medium, high, urgent
    response_time_minutes: Mapped[int] = mapped_column(Integer, default=60)
    resolution_time_minutes: Mapped[int] = mapped_column(Integer, default=480)
    is_active: Mapped[bool] = mapped_column(default=True)

class SLATracking(Base):
    __tablename__ = "sla_tracking"
    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("support_tickets.id"), unique=True)
    responded_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    resolved_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    breached: Mapped[bool] = mapped_column(default=False)
