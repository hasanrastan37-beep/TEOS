"""
سیستم ثبت گزارش‌های حسابرسی (Audit Log)
- ذخیره تمام تغییرات مهم در دیتابیس
- قابلیت جستجو و فیلتر
"""
from sqlalchemy import String, Integer, DateTime, Text, JSON, select, func
from sqlalchemy.orm import Mapped, mapped_column
from src.core.database import Base, async_session
from datetime import datetime
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    actor_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # کاربر انجام‌دهنده
    actor_role: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    action: Mapped[str] = mapped_column(String(128))  # مثلاً "user.create", "transaction.approve"
    target_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)  # "user", "transaction"
    target_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    success: Mapped[bool] = mapped_column(default=True)

class AuditService:
    @staticmethod
    async def log(db, actor_id: Optional[int], actor_role: Optional[str], action: str,
                  target_type: Optional[str] = None, target_id: Optional[str] = None,
                  details: Optional[dict] = None, ip: Optional[str] = None, success: bool = True):
        entry = AuditLog(
            actor_id=actor_id,
            actor_role=actor_role,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details or {},
            ip_address=ip,
            success=success,
            timestamp=datetime.utcnow()
        )
        db.add(entry)
        await db.commit()
        logger.info(f"Audit: {action} by {actor_id} on {target_type}:{target_id}")

    @staticmethod
    async def search(db, actor_id: Optional[int] = None, action: Optional[str] = None,
                     target_type: Optional[str] = None, limit: int = 100):
        stmt = select(AuditLog)
        if actor_id is not None:
            stmt = stmt.where(AuditLog.actor_id == actor_id)
        if action:
            stmt = stmt.where(AuditLog.action.ilike(f"%{action}%"))
        if target_type:
            stmt = stmt.where(AuditLog.target_type == target_type)
        stmt = stmt.order_by(AuditLog.timestamp.desc()).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

audit_service = AuditService()
