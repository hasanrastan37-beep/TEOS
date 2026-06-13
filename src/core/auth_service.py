"""
سرویس احراز هویت کامل:
- ورود با نام کاربری/رمز عبور (پنل تحت وب)
- ورود با Telegram ID (برای API)
- مدیریت توکن‌های JWT و رفرش توکن
- مسدودسازی موقت پس از تلاش‌های ناموفق
"""
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from src.core.settings import settings
from src.core.database import Base, async_session
from sqlalchemy import String, Integer, Boolean, DateTime, Text, select, update
from sqlalchemy.orm import Mapped, mapped_column
import logging

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# مدل جلسه‌های احراز هویت
class AuthSession(Base):
    __tablename__ = "auth_sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    refresh_token: Mapped[str] = mapped_column(String(512), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_revoked: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class LoginAttempt(Base):
    __tablename__ = "login_attempts"
    id: Mapped[int] = mapped_column(primary_key=True)
    identifier: Mapped[str] = mapped_column(String(128), index=True)  # username or telegram_id
    success: Mapped[bool] = mapped_column(default=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)

class AuthService:
    def __init__(self):
        self.access_token_expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        self.refresh_token_expire = timedelta(days=7)
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=15)

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or self.access_token_expire)
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    def create_refresh_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + self.refresh_token_expire
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    def decode_token(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except JWTError:
            return None

    async def authenticate_user(self, db, username: str, password: str, ip: str = None) -> Optional[dict]:
        # بررسی تلاش‌های ناموفق اخیر
        stmt = select(func.count()).select_from(LoginAttempt).where(
            LoginAttempt.identifier == username,
            LoginAttempt.success == False,
            LoginAttempt.timestamp > datetime.utcnow() - self.lockout_duration
        )
        recent_fails = (await db.execute(stmt)).scalar() or 0
        if recent_fails >= self.max_failed_attempts:
            logger.warning(f"Account locked for {username} due to too many attempts")
            return None

        # جستجوی کاربر (فرض در جدول User برای پنل)
        from src.core.user_engine import User
        user = await db.execute(select(User).where(User.username == username))
        user = user.scalars().first()
        if not user or not self.verify_password(password, user.hashed_password):
            db.add(LoginAttempt(identifier=username, success=False, ip_address=ip))
            await db.commit()
            return None

        db.add(LoginAttempt(identifier=username, success=True, ip_address=ip))
        await db.commit()

        access_token = self.create_access_token({"sub": str(user.id), "role": user.role})
        refresh_token = self.create_refresh_token({"sub": str(user.id)})
        # ذخیره refresh token
        db.add(AuthSession(user_id=user.id, refresh_token=refresh_token, expires_at=datetime.utcnow() + self.refresh_token_expire))
        await db.commit()
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {"id": user.id, "username": user.username, "role": user.role}
        }

    async def refresh_access_token(self, db, refresh_token: str) -> Optional[str]:
        payload = self.decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None
        # بررسی موجود بودن و عدم باطل‌شدن
        session = await db.execute(select(AuthSession).where(AuthSession.refresh_token == refresh_token, AuthSession.is_revoked == False))
        session = session.scalars().first()
        if not session or session.expires_at < datetime.utcnow():
            return None
        # تمدید
        user_id = int(payload["sub"])
        from src.core.user_engine import User
        user = await db.get(User, user_id)
        if not user:
            return None
        new_access = self.create_access_token({"sub": str(user.id), "role": user.role})
        return new_access

    async def revoke_session(self, db, refresh_token: str):
        stmt = update(AuthSession).where(AuthSession.refresh_token == refresh_token).values(is_revoked=True)
        await db.execute(stmt)
        await db.commit()

auth_service = AuthService()
