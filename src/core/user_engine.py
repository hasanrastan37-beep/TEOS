from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import Base, TimestampMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Integer, ForeignKey
import datetime

class User(TimestampMixin, Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(unique=True, index=True)
    username: Mapped[str] = mapped_column(String(64), nullable=True)
    full_name: Mapped[str] = mapped_column(String(128))
    role: Mapped[str] = mapped_column(String(32), default="user")  # user, admin_music, admin_vpn, owner
    is_blocked: Mapped[bool] = mapped_column(default=False)
    wallet_balance: Mapped[float] = mapped_column(default=0.0)

class RolePermission(Base):
    __tablename__ = "role_permissions"
    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[str] = mapped_column(String(32))
    permission: Mapped[str] = mapped_column(String(64))

async def get_user_by_telegram_id(db: AsyncSession, telegram_id: int) -> User | None:
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalars().first()

async def create_user_if_not_exists(db: AsyncSession, telegram_id: int, full_name: str, username: str = None) -> User:
    user = await get_user_by_telegram_id(db, telegram_id)
    if not user:
        user = User(telegram_id=telegram_id, full_name=full_name, username=username)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user
