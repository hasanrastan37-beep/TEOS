import pytest
from unittest.mock import AsyncMock, patch
from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update, Message, Chat, User

@pytest.fixture
def dispatcher():
    dp = Dispatcher(storage=MemoryStorage())
    # ثبت روترها
    from src.interfaces.telegram.handlers.start import start_router
    dp.include_router(start_router)
    return dp

@pytest.mark.asyncio
async def test_start_command(dispatcher):
    bot = AsyncMock(spec=Bot)
    user = User(id=12345, is_bot=False, first_name="Test")
    chat = Chat(id=12345, type="private")
    message = Message(message_id=1, date=datetime.now(), chat=chat, from_user=user, text="/start")
    # با استفاده از dp.feed_update
    await dispatcher.feed_update(bot, Update(update_id=1, message=message))
    bot.send_message.assert_called_once()
