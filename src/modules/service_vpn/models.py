from sqlalchemy import String, Text, Float, Boolean, Integer, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base, TimestampMixin
from typing import Optional, List
import enum
import datetime

class ServiceType(str, enum.Enum):
    VPN = "vpn"
    PROXY = "proxy"
    SERVER = "server"
    OTHER = "other"

class ServicePlan(Base, TimestampMixin):
    __tablename__ = "service_plans"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(256))
    type: Mapped[ServiceType] = mapped_column(default=ServiceType.VPN)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(Float)
    duration_days: Mapped[int] = mapped_column(Integer)  # مدت اعتبار
    data_limit_gb: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_featured: Mapped[bool] = mapped_column(default=False)
    max_clients: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # محدودیت تعداد کاربر همزمان
    tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    stock: Mapped[Optional[int]] = mapped_column(Integer, default=-1)  # موجودی نامحدود: -1
    category: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

class Order(Base, TimestampMixin):
    __tablename__ = "service_orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    plan_id: Mapped[int] = mapped_column(ForeignKey("service_plans.id"))
    quantity: Mapped[int] = mapped_column(default=1)
    total_price: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(32), default="pending")  # pending, paid, delivered, cancelled, refunded
    payment_method: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)  # wallet, direct
    delivery_info: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # کانفیگ تحویل داده شده
    valid_until: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    user = relationship("User", back_populates="orders")
    plan = relationship("ServicePlan")

# اضافه کردن relation در User (در فایل user_engine.py هم اضافه می‌شود)
