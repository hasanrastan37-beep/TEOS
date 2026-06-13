from sqlalchemy import String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from src.core.database import Base
import datetime

class ABTest(Base):
    __tablename__ = "ab_tests"
    id: Mapped[int] = mapped_column(primary_key=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("marketing_campaigns.id"))
    variant_a: Mapped[str] = mapped_column(Text)  # متن
    variant_b: Mapped[str] = mapped_column(Text)
    impressions_a: Mapped[int] = mapped_column(default=0)
    impressions_b: Mapped[int] = mapped_column(default=0)
    conversions_a: Mapped[int] = mapped_column(default=0)
    conversions_b: Mapped[int] = mapped_column(default=0)
    winner_variant: Mapped[str] = mapped_column(String(1), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
