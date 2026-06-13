from sqlalchemy import String, Integer, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.core.database import Base, TimestampMixin
from typing import Optional
import datetime

class VPNServer(Base):
    __tablename__ = "vpn_servers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    ip_address: Mapped[str] = mapped_column(String(45))
    location: Mapped[str] = mapped_column(String(128))
    is_active: Mapped[bool] = mapped_column(default=True)
    total_slots: Mapped[int] = mapped_column(default=50)
    used_slots: Mapped[int] = mapped_column(default=0)
    last_health_check: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))

class WireGuardConfig(Base):
    __tablename__ = "wireguard_configs"
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("service_orders.id"))
    server_id: Mapped[int] = mapped_column(ForeignKey("vpn_servers.id"))
    private_key: Mapped[str] = mapped_column(Text)
    public_key: Mapped[str] = mapped_column(Text)
    assigned_ip: Mapped[str] = mapped_column(String(45))
    config_text: Mapped[str] = mapped_column(Text)  # فایل کانفیگ کامل
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
