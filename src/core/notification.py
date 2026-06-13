from typing import Any
import logging

logger = logging.getLogger(__name__)

async def notify_user(user_id: int, message: str, **kwargs):
    # از طریق ربات تلگرام ارسال شود. برای سادگی فعلی یک شبیه‌سازی.
    logger.info(f"Notification to user {user_id}: {message}")
    # در محیط واقعی: await bot.send_message(chat_id=user_id, text=message)
