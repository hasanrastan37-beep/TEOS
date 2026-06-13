from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base, TimestampMixin
import datetime

class ReferralCode(Base):
    __tablename__ = "referral_codes_v2"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    campaign_id: Mapped[Optional[int]] = mapped_column(ForeignKey("marketing_campaigns_v2.id"), nullable=True)
    total_uses: Mapped[int] = mapped_column(default=0)
    max_uses: Mapped[Optional[int]] = mapped_column(nullable=True)
    reward_per_signup: Mapped[float] = mapped_column(default=0.0)
    reward_per_purchase: Mapped[float] = mapped_column(default=0.0)
    is_active: Mapped[bool] = mapped_column(default=True)
    expires_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    owner = relationship("User", foreign_keys=[owner_id])
    campaign = relationship("MarketingCampaign")

class ReferralEvent(Base):
    __tablename__ = "referral_events"
    id: Mapped[int] = mapped_column(primary_key=True)
    code_id: Mapped[int] = mapped_column(ForeignKey("referral_codes_v2.id"))
    referred_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    event_type: Mapped[str] = mapped_column(String(32))  # signup, purchase, etc.
    reward_amount: Mapped[float] = mapped_column(default=0.0)
    rewarded: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    code = relationship("ReferralCode")
    referred_user = relationship("User", foreign_keys=[referred_user_id])
