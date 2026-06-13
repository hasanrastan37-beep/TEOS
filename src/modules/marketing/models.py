from sqlalchemy import String, Text, DateTime, Boolean, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base, TimestampMixin
from typing import Optional, List
import datetime

class Campaign(Base, TimestampMixin):
    __tablename__ = "marketing_campaigns"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(256))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    message_template: Mapped[str] = mapped_column(Text)  # قالب با placeholders
    status: Mapped[str] = mapped_column(String(32), default="draft")  # draft, active, paused, completed
    scheduled_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    target_filter: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Rule Engine فیلتر مخاطبان
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    creator = relationship("User")
    
class CampaignRecipient(Base):
    __tablename__ = "marketing_recipients"
    id: Mapped[int] = mapped_column(primary_key=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("marketing_campaigns.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    sent_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(32), default="pending")  # pending, sent, failed
    campaign = relationship("Campaign")
    user = relationship("User")
