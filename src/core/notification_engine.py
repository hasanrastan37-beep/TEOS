"""
موتور اعلان‌های پیشرفته:
- ارسال پیام به کاربر از طریق ربات
- ارسال به کانال‌ها
- ذخیره و مدیریت قالب‌ها
- صف‌بندی و retry
"""
from sqlalchemy import String, Text, Boolean, Integer, JSON, select
from sqlalchemy.orm import Mapped, mapped_column
from src.core.database import Base, async_session
from src.interfaces.telegram.bot import get_bot  # تابع کمکی برای گرفتن نمونه bot
from typing import Optional, Dict
import asyncio
import logging

logger = logging.getLogger(__name__)

class NotificationTemplate(Base):
    __tablename__ = "notification_templates"
    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(64), unique=True)
    title: Mapped[str] = mapped_column(String(128))
    body_template: Mapped[str] = mapped_column(Text)
    variables: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # توضیحات متغیرها
    is_active: Mapped[bool] = mapped_column(default=True)

class NotificationService:
    async def send(self, user_id: int, template_key: str, variables: Optional[Dict[str, str]] = None, **kwargs):
        async with async_session() as db:
            template = await db.execute(select(NotificationTemplate).where(NotificationTemplate.key == template_key))
            template = template.scalars().first()
            if not template or not template.is_active:
                logger.error(f"Template {template_key} not found or inactive")
                return False
            try:
                text = template.body_template
                if variables:
                    for k, v in variables.items():
                        text = text.replace(f"{{{{{k}}}}}", str(v))
                # ارسال با bot
                bot = get_bot()
                if bot:
                    await bot.send_message(chat_id=user_id, text=text, **kwargs)
                    return True
            except Exception as e:
                logger.exception(f"Failed to send notification to {user_id}: {e}")
                return False
        return False

notification_service = NotificationService()
