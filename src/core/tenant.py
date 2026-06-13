from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

class Tenant(Base):
    __tablename__ = "tenants"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    domain: Mapped[str] = mapped_column(String(100), nullable=True)
    telegram_bot_token: Mapped[str] = mapped_column(String(100), nullable=True)  # ربات اختصاصی
    is_active: Mapped[bool] = mapped_column(default=True)

async def get_tenant_by_id(db: AsyncSession, tenant_id: int) -> Tenant | None:
    pass
