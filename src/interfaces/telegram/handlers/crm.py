from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import async_session
from src.modules.crm.service import crm_service, LeadStatus

crm_router = Router()

@crm_router.message(Command("leads"))
async def list_leads_command(message: types.Message):
    # فقط ادمین
    async with async_session() as db:
        leads = await crm_service.list_leads(db, page=1, page_size=10)
    if not leads:
        await message.answer("هیچ لید یافت نشد.")
        return
    text = "📊 لیدها:\n\n"
    for l in leads:
        text += f"🔹 {l.first_name} {l.last_name or ''} - وضعیت: {l.status.value}\n"
    await message.answer(text)
