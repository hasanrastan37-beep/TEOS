"""
هندلرهای پیشرفتهٔ موزیک:
- صفحه‌بندی (pagination) با inline buttons
- جستجوی زنده
- افزودن به علاقه‌مندی‌ها
- آپلود و مدیریت از طریق ربات
"""
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import async_session
from src.modules.music.models import Track
from src.modules.music.service import music_service
from src.core.user_engine import get_user_by_telegram_id
from typing import List, Optional
import math

music_advanced_router = Router()

ITEMS_PER_PAGE = 5

@music_advanced_router.callback_query(F.data == "music_top_paginated")
async def top_tracks_paginated(callback: types.CallbackQuery, page: int = 0):
    async with async_session() as db:
        offset = page * ITEMS_PER_PAGE
        tracks = await music_service.get_top_tracks_paginated(db, limit=ITEMS_PER_PAGE, offset=offset)
        total = await music_service.get_total_tracks(db)
        total_pages = math.ceil(total / ITEMS_PER_PAGE)
    if not tracks:
        await callback.message.edit_text("هیچ آهنگی موجود نیست.")
        return
    text = "🎼 برترین آهنگ‌ها:\n\n"
    for idx, track in enumerate(tracks, start=1):
        text += f"{idx}. {track.title} - {track.artist} (▶️ {track.plays})\n"
    builder = InlineKeyboardBuilder()
    # دکمه‌های صفحه‌بندی
    row = []
    if page > 0:
        row.append(InlineKeyboardButton(text="⬅️ قبلی", callback_data=f"music_top_page_{page-1}"))
    if page < total_pages - 1:
        row.append(InlineKeyboardButton(text="بعدی ➡️", callback_data=f"music_top_page_{page+1}"))
    if row:
        builder.row(*row)
    builder.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="menu_music"))
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()

@music_advanced_router.callback_query(F.data.startswith("music_top_page_"))
async def top_tracks_page_callback(callback: types.CallbackQuery):
    page = int(callback.data.split("_")[-1])
    await top_tracks_paginated(callback, page)

@music_advanced_router.callback_query(F.data == "music_search")
async def music_search_prompt(callback: types.CallbackQuery):
    await callback.message.answer("🎤 نام آهنگ یا خواننده را وارد کنید:")
    await callback.answer()
    # در عمل از FSM برای دریافت پیام بعدی استفاده می‌شود (اینجا فقط جهت نمایش)

@music_advanced_router.message(Command("search"))
async def search_command(message: types.Message):
    query = message.text.replace("/search", "").strip()
    if not query:
        await message.answer("لطفاً عبارت جستجو را وارد کنید.")
        return
    async with async_session() as db:
        results = await music_service.search_tracks(db, query)
    if not results:
        await message.answer("نتیجه‌ای یافت نشد.")
        return
    text = "نتایج جستجو:\n"
    for t in results[:10]:
        text += f"🎵 {t.title} - {t.artist}\n"
    await message.answer(text)

# علاقه‌مندی‌ها (favorites) – ذخیره در دیتابیس
class Favorite(Base):
    __tablename__ = "user_favorites"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    track_id: Mapped[int] = mapped_column(ForeignKey("tracks.id"), primary_key=True)

async def toggle_favorite(db: AsyncSession, user_id: int, track_id: int) -> bool:
    fav = await db.get(Favorite, (user_id, track_id))
    if fav:
        await db.delete(fav)
        await db.commit()
        return False  # حذف شد
    else:
        db.add(Favorite(user_id=user_id, track_id=track_id))
        await db.commit()
        return True  # اضافه شد

@music_advanced_router.callback_query(F.data.startswith("fav_"))
async def toggle_fav_handler(callback: types.CallbackQuery):
    track_id = int(callback.data.split("_")[1])
    async with async_session() as db:
        user = await get_user_by_telegram_id(db, callback.from_user.id)
        if not user:
            await callback.answer("کاربر یافت نشد.")
            return
        added = await toggle_favorite(db, user.id, track_id)
    await callback.answer("به علاقه‌مندی‌ها اضافه شد." if added else "از علاقه‌مندی‌ها حذف شد.")
