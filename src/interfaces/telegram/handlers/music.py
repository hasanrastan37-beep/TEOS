from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.core.database import async_session
from src.modules.music.service import music_service

music_router = Router()

@music_router.callback_query(F.data == "menu_music")
async def show_music_menu(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🎵 آهنگ‌های برتر", callback_data="music_top"))
    builder.row(types.InlineKeyboardButton(text="🔍 جستجوی آهنگ", switch_inline_query_current_chat=""))
    builder.row(types.InlineKeyboardButton(text="🎧 آهنگ‌های جدید", callback_data="music_new"))
    builder.row(types.InlineKeyboardButton(text="📂 دسته‌بندی‌ها", callback_data="music_genres"))
    await callback.message.edit_text("🎶 بخش موزیک", reply_markup=builder.as_markup())
    await callback.answer()

@music_router.callback_query(F.data == "music_top")
async def top_tracks(callback: types.CallbackQuery):
    async with async_session() as db:
        tracks = await music_service.top_tracks(db, limit=5)
        if not tracks:
            await callback.message.answer("آهنگ برتری یافت نشد.")
            return
        text = "🎼 برترین آهنگ‌ها:\n\n"
        for t in tracks:
            text += f"🎵 {t.title} - {t.artist}\n"
        await callback.message.answer(text)
    await callback.answer()
