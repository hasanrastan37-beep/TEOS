"""
میدلورهای امنیتی:
- Rate Limiting بر اساس کاربر
- Anti-Flood (جلوگیری از اسپم)
- تشخیص محتوای مخرب (ساده)
- مسدودسازی خودکار کاربران متخلف
"""
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update
from collections import defaultdict
from datetime import datetime, timedelta
import re
import logging
from src.core.settings import settings
from src.core.database import async_session
from src.core.user_engine import User, get_user_by_telegram_id

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, max_calls: int = 30, period: int = 60):
        self.max_calls = max_calls
        self.period = period  # ثانیه
        self.calls = defaultdict(list)

    def is_limited(self, user_id: int) -> bool:
        now = datetime.now()
        self.calls[user_id] = [t for t in self.calls[user_id] if now - t < timedelta(seconds=self.period)]
        if len(self.calls[user_id]) >= self.max_calls:
            return True
        self.calls[user_id].append(now)
        return False

class AntiSpamMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self.rate_limiter = RateLimiter(max_calls=20, period=60)  # ۲۰ درخواست در دقیقه
        self.message_history = defaultdict(list)  # ذخیره پیام‌های اخیر برای تشخیص تکرار
        self.blocked_patterns = [
            re.compile(r"(buy|sell|cheap|discount).*(http|www|\.com)", re.IGNORECASE),
            re.compile(r"https?://\S+", re.IGNORECASE),  # لینک‌ها (می‌توان محدود کرد)
        ]

    async def __call__(self, handler, event: Update, data: dict):
        user_id = None
        if event.message:
            user_id = event.message.from_user.id
            text = event.message.text or ""
        elif event.callback_query:
            user_id = event.callback_query.from_user.id
            text = event.callback_query.data or ""
        else:
            return await handler(event, data)

        if not user_id:
            return await handler(event, data)

        # Rate Limit Check
        if self.rate_limiter.is_limited(user_id):
            logger.warning(f"Rate limit exceeded for user {user_id}")
            if event.message:
                await event.message.answer("⏳ شما بیش از حد مجاز درخواست ارسال کرده‌اید. لطفاً کمی صبر کنید.")
            return

        # Anti-Flood: پیام‌های تکراری
        if text:
            self.message_history[user_id].append((text, datetime.now()))
            # نگهداری فقط ۵ پیام آخر
            self.message_history[user_id] = self.message_history[user_id][-5:]
            # اگر ۴ پیام یکسان در ۱۰ ثانیه
            recent_same = sum(1 for t, ts in self.message_history[user_id] if t == text and (datetime.now() - ts).total_seconds() < 10)
            if recent_same >= 4:
                logger.warning(f"Flood detected for user {user_id}")
                await self._block_user(user_id)
                if event.message:
                    await event.message.answer("⛔ شما به دلیل ارسال اسپم مسدود شدید.")
                return

        # تشخیص لینک‌های مخرب (ساده)
        if event.message and any(pattern.search(text) for pattern in self.blocked_patterns):
            # اجازه ندهیم یا هشدار
            await event.message.answer("⚠️ ارسال لینک مجاز نیست.")
            return

        return await handler(event, data)

    async def _block_user(self, user_id: int):
        async with async_session() as db:
            user = await get_user_by_telegram_id(db, user_id)
            if user:
                user.is_blocked = True
                await db.commit()
                logger.info(f"User {user_id} blocked automatically.")
