from sqlalchemy import String, Text, Float, Integer, Boolean, DateTime, ForeignKey, JSON, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base, TimestampMixin
import enum
import datetime

class CampaignType(str, enum.Enum):
    TELEGRAM = "telegram"
    EMAIL = "email"
    SMS = "sms"

class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class MarketingCampaign(Base, TimestampMixin):
    __tablename__ = "marketing_campaigns_v2"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(256))
    type: Mapped[CampaignType] = mapped_column(default=CampaignType.TELEGRAM)
    status: Mapped[CampaignStatus] = mapped_column(default=CampaignStatus.DRAFT)
    subject: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)  # برای ایمیل
    body_template: Mapped[str] = mapped_column(Text)
    scheduled_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    target_segment: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Rule Engine filter
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    total_sent: Mapped[int] = mapped_column(default=0)
    total_delivered: Mapped[int] = mapped_column(default=0)
    total_opened: Mapped[int] = mapped_column(default=0)
    total_clicked: Mapped[int] = mapped_column(default=0)
    total_converted: Mapped[int] = mapped_column(default=0)
    creator = relationship("User")

class ABTestCampaign(Base):
    __tablename__ = "ab_test_campaigns"
    id: Mapped[int] = mapped_column(primary_key=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("marketing_campaigns_v2.id"))
    variant_a_subject: Mapped[str] = mapped_column(String(256))
    variant_a_body: Mapped[str] = mapped_column(Text)
    variant_b_subject: Mapped[str] = mapped_column(String(256))
    variant_b_body: Mapped[str] = mapped_column(Text)
    split_ratio: Mapped[float] = mapped_column(Float, default=0.5)  # سهم A
    impressions_a: Mapped[int] = mapped_column(default=0)
    impressions_b: Mapped[int] = mapped_column(default=0)
    conversions_a: Mapped[int] = mapped_column(default=0)
    conversions_b: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(default=True)
    campaign = relationship("MarketingCampaign")
