from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import async_session
from src.core.user_engine import User, get_user_by_telegram_id
from src.modules.music.service import music_service
from src.modules.music.models import Track
from src.modules.service_vpn.service import vpn_service
from src.modules.service_vpn.models import ServicePlan, Order
from src.modules.wallet_payment.service import wallet_service
from src.modules.support_ticket.service import ticket_service

admin_router = Router()

# ----- منوی اصلی ادمین -----
@admin_router.message(Command("admin"))
async def admin_main(message: types.Message):
    async with async_session() as db:
        user = await get_user_by_telegram_id(db, message.from_user.id)
        if not user or user.role not in ["admin_music", "admin_vpn", "owner"]:
            await message.answer("⛔ دسترسی غیرمجاز")
            return
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🎵 مدیریت موزیک", callback_data="admin_music"))
    builder.row(types.InlineKeyboardButton(text="🛠 مدیریت سرویس‌ها", callback_data="admin_vpn"))
    builder.row(types.InlineKeyboardButton(text="👥 مدیریت کاربران", callback_data="admin_users"))
    builder.row(types.InlineKeyboardButton(text="💰 تراکنش‌های در انتظار", callback_data="admin_pending_tx"))
    builder.row(types.InlineKeyboardButton(text="🎫 تیکت‌ها", callback_data="admin_tickets"))
    await message.answer("🛡 پنل ادمین", reply_markup=builder.as_markup())

# ----- مدیریت موزیک -----
class AddTrackState(StatesGroup):
    waiting_for_title = State()
    waiting_for_artist = State()
    waiting_for_file = State()

@admin_router.callback_query(F.data == "admin_music")
async def admin_music_menu(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="➕ افزودن آهنگ", callback_data="admin_add_track"))
    builder.row(types.InlineKeyboardButton(text="📋 لیست آهنگ‌ها", callback_data="admin_list_tracks"))
    builder.row(types.InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin_main"))
    await callback.message.edit_text("🎵 مدیریت موزیک", reply_markup=builder.as_markup())
    await callback.answer()

@admin_router.callback_query(F.data == "admin_add_track")
async def add_track_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("عنوان آهنگ را وارد کنید:")
    await state.set_state(AddTrackState.waiting_for_title)
    await callback.answer()

@admin_router.message(AddTrackState.waiting_for_title)
async def add_track_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("نام هنرمند را وارد کنید:")
    await state.set_state(AddTrackState.waiting_for_artist)

@admin_router.message(AddTrackState.waiting_for_artist)
async def add_track_artist(message: types.Message, state: FSMContext):
    await state.update_data(artist=message.text)
    await message.answer("فایل صوتی را ارسال کنید (MP3).")
    await state.set_state(AddTrackState.waiting_for_file)

@admin_router.message(AddTrackState.waiting_for_file, F.audio)
async def add_track_file(message: types.Message, state: FSMContext):
    data = await state.get_data()
    title = data['title']
    artist = data['artist']
    file_id = message.audio.file_id
    async with async_session() as db:
        track = Track(title=title, artist=artist, file_id=file_id)
        db.add(track)
        await db.commit()
    await message.answer("✅ آهنگ با موفقیت افزوده شد.")
    await state.clear()

@admin_router.callback_query(F.data == "admin_list_tracks")
async def admin_list_tracks(callback: types.CallbackQuery):
    async with async_session() as db:
        tracks = await music_service.top_tracks(db, limit=15)  # اخیراً اضافه شده
    if not tracks:
        await callback.message.answer("هیچ آهنگی یافت نشد.")
        return
    builder = InlineKeyboardBuilder()
    for t in tracks:
        builder.row(types.InlineKeyboardButton(
            text=f"{t.title[:30]} - {t.artist[:20]}",
            callback_data=f"admin_track_{t.id}"
        ))
    builder.row(types.InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin_music"))
    await callback.message.edit_text("📋 لیست آهنگ‌ها (برای حذف/ویرایش کلیک کنید)", reply_markup=builder.as_markup())
    await callback.answer()

@admin_router.callback_query(F.data.startswith("admin_track_"))
async def admin_track_detail(callback: types.CallbackQuery):
    track_id = int(callback.data.split("_")[-1])
    async with async_session() as db:
        track = await db.get(Track, track_id)
    if not track:
        await callback.answer("یافت نشد")
        return
    status = "فعال" if track.is_active else "غیرفعال"
    text = f"🎵 {track.title}\n👤 {track.artist}\n▶️ {track.plays} پخش\n❤️ {track.likes} لایک\n📌 وضعیت: {status}"
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="❌ حذف (غیرفعال‌سازی)", callback_data=f"admin_track_delete_{track.id}"))
    builder.row(types.InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin_list_tracks"))
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()

@admin_router.callback_query(F.data.startswith("admin_track_delete_"))
async def admin_track_delete(callback: types.CallbackQuery):
    track_id = int(callback.data.split("_")[-1])
    async with async_session() as db:
        track = await db.get(Track, track_id)
        if track:
            track.is_active = False
            await db.commit()
    await callback.answer("آهنگ غیرفعال شد.")
    # بازگشت به لیست
    await admin_list_tracks(callback)

# ----- مدیریت سرویس‌ها (ادمین VPN) -----
@admin_router.callback_query(F.data == "admin_vpn")
async def admin_vpn_menu(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="➕ افزودن پلن", callback_data="admin_add_plan"))
    builder.row(types.InlineKeyboardButton(text="📋 پلن‌های موجود", callback_data="admin_list_plans"))
    builder.row(types.InlineKeyboardButton(text="📦 سفارشات", callback_data="admin_orders"))
    builder.row(types.InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin_main"))
    await callback.message.edit_text("🛠 مدیریت سرویس‌ها", reply_markup=builder.as_markup())
    await callback.answer()

# (جهت جلوگیری از طولانی‌شدن، جزئیات افزودن پلن مشابه موزیک است)
# ...

# ----- مدیریت کاربران -----
@admin_router.callback_query(F.data == "admin_users")
async def admin_users_list(callback: types.CallbackQuery):
    async with async_session() as db:
        stmt = select(User).order_by(User.id.desc()).limit(20)
        result = await db.execute(stmt)
        users = result.scalars().all()
    if not users:
        await callback.message.answer("هیچ کاربری یافت نشد.")
        return
    builder = InlineKeyboardBuilder()
    for u in users:
        builder.row(types.InlineKeyboardButton(
            text=f"{u.full_name} ({u.role})",
            callback_data=f"admin_user_{u.id}"
        ))
    builder.row(types.InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin_main"))
    await callback.message.edit_text("👥 کاربران", reply_markup=builder.as_markup())
    await callback.answer()

@admin_router.callback_query(F.data.startswith("admin_user_"))
async def admin_user_detail(callback: types.CallbackQuery):
    uid = int(callback.data.split("_")[-1])
    async with async_session() as db:
        user = await db.get(User, uid)
    if not user:
        await callback.answer("یافت نشد")
        return
    text = f"👤 {user.full_name}\n🆔 {user.telegram_id}\n🎭 {user.role}\n🚫 مسدود: {'بله' if user.is_blocked else 'خیر'}"
    builder = InlineKeyboardBuilder()
    if user.role != "owner":
        builder.row(types.InlineKeyboardButton(text="🚫 مسدود کردن", callback_data=f"admin_block_{user.id}"))
        builder.row(types.InlineKeyboardButton(text="ارتقا به ادمین موزیک", callback_data=f"admin_promote_music_{user.id}"))
    builder.row(types.InlineKeyboardButton(text="🔙 بازگشت", callback_data="admin_users"))
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()
