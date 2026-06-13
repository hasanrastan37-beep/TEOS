from sqlalchemy import String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base, TimestampMixin
import datetime

class BulkOrder(Base, TimestampMixin):
    __tablename__ = "bulk_orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    plan_id: Mapped[int] = mapped_column(ForeignKey("service_plans.id"))
    quantity: Mapped[int] = mapped_column(Integer)
    total_price: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(32), default="pending")  # pending, confirmed, delivered
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # جزئیات بیشتر
    delivery_emails: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # لیست ایمیل‌ها
    custom_configs: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
