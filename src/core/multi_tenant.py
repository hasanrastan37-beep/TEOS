from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from src.core.database import Base
from contextvars import ContextVar

current_tenant_id: ContextVar[int] = ContextVar("current_tenant_id", default=None)

class Tenant(Base):
    __tablename__ = "tenants"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    telegram_bot_token: Mapped[str] = mapped_column(String(100))  # ربات اختصاصی
    is_active: Mapped[bool] = mapped_column(default=True)
