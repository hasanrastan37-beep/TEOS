from aiogram import Bot
from src.core.settings import settings

class ChannelManager:
    def __init__(self):
        self.bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

    async def send_to_channel(self, channel_id: str, text: str, parse_mode: str = "HTML"):
        await self.bot.send_message(chat_id=channel_id, text=text, parse_mode=parse_mode)

    async def broadcast(self, user_ids: list[int], text: str):
        for uid in user_ids:
            try:
                await self.bot.send_message(uid, text)
            except Exception as e:
                continue
