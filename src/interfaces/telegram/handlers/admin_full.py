"""
پنل کامل ادمین تلگرام
شامل: مدیریت آهنگ‌ها، کاربران، سرویس‌ها، تراکنش‌ها، تیکت‌ها، پیام‌های انبوه، آمار، تنظیمات ادمین
"""
from aiogram import Router, F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, update, delete
from src.core.database import async_session, get_db
from src.core.user_engine import User, get_user_by_telegram_id, create_user_if_not_exists
from src.modules.music.models import Track
from src.modules.music.service import music_service
from src.modules.service_vpn.models import ServicePlan, Order
from src.modules.service_vpn.service import vpn_service
from src.modules.wallet_payment.models import Transaction, TransactionStatus, TransactionType
from src.modules.wallet_payment.service import wallet_service
from src.modules.support_ticket.models import Ticket, TicketMessage, TicketStatus, TicketPriority
from src.modules.support_ticket.service import ticket_service
from src.modules.crm.models import Lead, LeadStatus
from src.modules.analytics.service import analytics_service
from src.core.menu_engine import MenuNode, menu_engine
from src.core.events import event_bus, Event
from src.core.rule_engine import RuleEngine
from typing import Optional, List
import datetime
import logging

logger = logging.getLogger(__name__)
admin_full_router = Router()

# -------------- FSM States --------------
class AddTrackFSM(StatesGroup):
    waiting_title = State()
    waiting_artist = State()
    waiting_genre = State()
    waiting_file = State()
    waiting_tags = State()

class AddPlanFSM(StatesGroup):
    waiting_name = State()
    waiting_type = State()
    waiting_price = State()
    waiting_duration = State()
    waiting_description = State()

class BroadcastFSM(StatesGroup):
    waiting_message = State()
    waiting_filter = State()
    confirm = State()

class ModifyUserFSM(StatesGroup):
    selecting_user = State()
    choosing_action = State()
    entering_value = State()

# -------------- Helper: Check admin role --------------
async def require_admin(message: types.Message, required_roles: list = None):
    async with async_session() as db:
        user = await get_user_by_telegram_id(db, message.from_user.id)
        if not user or user.role not in (required_roles or ["admin_music", "admin_vpn", "owner"]):
            await message.answer("⛔ دسترسی غیرمجاز. شما ادمین نیستید یا سطح دسترسی کافی ندارید.")
            return None
    return user

# -------------- Main Admin Menu --------------
@admin_full_router.message(Command("admin"))
async def cmd_admin(message: types.Message):
    user = await require_admin(message)
    if not user:
        return
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🎵 مدیریت موزیک", callback_data="adm_music_menu"))
    builder.row(InlineKeyboardButton(text="🌐 مدیریت سرویس‌ها", callback_data="adm_vpn_menu"))
    builder.row(InlineKeyboardButton(text="👥 مدیریت کاربران", callback_data="adm_users_menu"))
    builder.row(InlineKeyboardButton(text="💰 تراکنش‌های در انتظار", callback_data="adm_pending_tx"))
    builder.row(InlineKeyboardButton(text="🎫 تیکت‌ها", callback_data="adm_tickets_menu"))
    builder.row(InlineKeyboardButton(text="📊 آمار سریع", callback_data="adm_stats"))
    builder.row(InlineKeyboardButton(text="📢 ارسال پیام گروهی", callback_data="adm_broadcast"))
    builder.row(InlineKeyboardButton(text="🔐 تنظیمات ادمین", callback_data="adm_settings"))
    await message.answer("🛡 پنل مدیریت TEOS", reply_markup=builder.as_markup())

# -------------- Music Management --------------
@admin_full_router.callback_query(F.data == "adm_music_menu")
async def music_menu(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="➕ افزودن آهنگ", callback_data="adm_add_track"))
    builder.row(InlineKeyboardButton(text="📋 لیست آهنگ‌ها", callback_data="adm_list_tracks"))
    builder.row(InlineKeyboardButton(text="🗑 حذف (غیرفعال‌سازی) آهنگ", callback_data="adm_delete_track"))
    builder.row(InlineKeyboardButton(text="✏️ ویرایش آهنگ", callback_data="adm_edit_track"))
    builder.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="adm_main"))
    await callback.message.edit_text("🎵 مدیریت موزیک", reply_markup=builder.as_markup())
    await callback.answer()

@admin_full_router.callback_query(F.data == "adm_add_track")
async def add_track_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("عنوان آهنگ را وارد کنید:")
    await state.set_state(AddTrackFSM.waiting_title)
    await callback.answer()

@admin_full_router.message(AddTrackFSM.waiting_title)
async def add_track_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await message.answer("نام هنرمند:")
    await state.set_state(AddTrackFSM.waiting_artist)

@admin_full_router.message(AddTrackFSM.waiting_artist)
async def add_track_artist(message: types.Message, state: FSMContext):
    await state.update_data(artist=message.text.strip())
    await message.answer("ژانر (اختیاری، مثال: pop, rock):")
    await state.set_state(AddTrackFSM.waiting_genre)

@admin_full_router.message(AddTrackFSM.waiting_genre)
async def add_track_genre(message: types.Message, state: FSMContext):
    await state.update_data(genre=message.text.strip())
    await message.answer("فایل صوتی (MP3) را ارسال کنید:")
    await state.set_state(AddTrackFSM.waiting_file)

@admin_full_router.message(AddTrackFSM.waiting_file, F.audio)
async def add_track_file(message: types.Message, state: FSMContext):
    data = await state.get_data()
    file_id = message.audio.file_id
    await state.update_data(file_id=file_id)
    await message.answer("برچسب‌ها (اختیاری، با کاما جدا کنید):")
    await state.set_state(AddTrackFSM.waiting_tags)

@admin_full_router.message(AddTrackFSM.waiting_tags)
async def add_track_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    tags = message.text.strip() if message.text else None
    async with async_session() as db:
        track = Track(
            title=data['title'],
            artist=data['artist'],
            genre=data.get('genre'),
            file_id=data.get('file_id'),
            tags=tags,
            is_active=True
        )
        db.add(track)
        await db.commit()
        await event_bus.publish(Event(name="track.created", payload={"track_id": track.id}))
    await message.answer(f"✅ آهنگ «{track.title}» با موفقیت افزوده شد.")
    await state.clear()

# لیست آهنگ‌ها با صفحه‌بندی
@admin_full_router.callback_query(F.data.startswith("adm_list_tracks"))
async def admin_list_tracks(callback: types.CallbackQuery):
    page = int(callback.data.split(":")[-1]) if ":" in callback.data else 0
    per_page = 8
    async with async_session() as db:
        stmt = select(Track).order_by(Track.id.desc()).offset(page * per_page).limit(per_page)
        result = await db.execute(stmt)
        tracks = result.scalars().all()
        total = (await db.execute(select(func.count()).select_from(Track))).scalar()
        total_pages = max(1, (total + per_page - 1) // per_page)
    if not tracks:
        await callback.message.edit_text("هیچ آهنگی موجود نیست.")
        return
    text = f"📋 لیست آهنگ‌ها (صفحه {page+1}/{total_pages}):\n\n"
    for t in tracks:
        status = "✅" if t.is_active else "❌"
        text += f"{status} {t.id}: {t.title[:30]} - {t.artist[:20]} | {t.plays}▶️\n"
    builder = InlineKeyboardBuilder()
    row = []
    if page > 0:
        row.append(InlineKeyboardButton(text="⬅️ قبلی", callback_data=f"adm_list_tracks:{page-1}"))
    if page < total_pages - 1:
        row.append(InlineKeyboardButton(text="بعدی ➡️", callback_data=f"adm_list_tracks:{page+1}"))
    if row:
        builder.row(*row)
    builder.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="adm_music_menu"))
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()

# -------------- VPN/Service Management (افزودن پلن) --------------
@admin_full_router.callback_query(F.data == "adm_vpn_menu")
async def vpn_menu(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="➕ افزودن پلن", callback_data="adm_add_plan"))
    builder.row(InlineKeyboardButton(text="📋 پلن‌های موجود", callback_data="adm_list_plans"))
    builder.row(InlineKeyboardButton(text="📦 سفارشات", callback_data="adm_orders"))
    builder.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="adm_main"))
    await callback.message.edit_text("🌐 مدیریت سرویس‌ها", reply_markup=builder.as_markup())
    await callback.answer()

@admin_full_router.callback_query(F.data == "adm_add_plan")
async def add_plan_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("نام پلن را وارد کنید:")
    await state.set_state(AddPlanFSM.waiting_name)
    await callback.answer()

@admin_full_router.message(AddPlanFSM.waiting_name)
async def add_plan_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("نوع پلن (vpn / proxy / server / other):")
    await state.set_state(AddPlanFSM.waiting_type)

@admin_full_router.message(AddPlanFSM.waiting_type)
async def add_plan_type(message: types.Message, state: FSMContext):
    await state.update_data(plan_type=message.text.strip())
    await message.answer("قیمت (تومان):")
    await state.set_state(AddPlanFSM.waiting_price)

@admin_full_router.message(AddPlanFSM.waiting_price)
async def add_plan_price(message: types.Message, state: FSMContext):
    try:
        price = float(message.text)
    except ValueError:
        await message.answer("مبلغ نامعتبر. یک عدد وارد کنید.")
        return
    await state.update_data(price=price)
    await message.answer("مدت (روز):")
    await state.set_state(AddPlanFSM.waiting_duration)

@admin_full_router.message(AddPlanFSM.waiting_duration)
async def add_plan_duration(message: types.Message, state: FSMContext):
    try:
        dur = int(message.text)
    except ValueError:
        await message.answer("مدت نامعتبر.")
        return
    await state.update_data(duration_days=dur)
    await message.answer("توضیحات (اختیاری، یا /skip):")
    await state.set_state(AddPlanFSM.waiting_description)

@admin_full_router.message(AddPlanFSM.waiting_description)
async def add_plan_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    desc = message.text.strip() if message.text != "/skip" else None
    async with async_session() as db:
        plan = ServicePlan(
            name=data['name'],
            type=data['plan_type'],
            price=data['price'],
            duration_days=data['duration_days'],
            description=desc,
            is_active=True
        )
        db.add(plan)
        await db.commit()
    await message.answer("✅ پلن با موفقیت اضافه شد.")
    await state.clear()

# -------------- Transactions (تأیید/رد) --------------
@admin_full_router.callback_query(F.data == "adm_pending_tx")
async def pending_transactions(callback: types.CallbackQuery):
    async with async_session() as db:
        stmt = select(Transaction).where(Transaction.status == TransactionStatus.PENDING).order_by(Transaction.created_at.desc()).limit(10)
        result = await db.execute(stmt)
        txs = result.scalars().all()
    if not txs:
        await callback.message.edit_text("هیچ تراکنش در انتظاری نیست.")
        return
    text = "💰 تراکنش‌های در انتظار:\n"
    for tx in txs:
        text += f"\n🔹 {tx.id}: {tx.amount} تومان | {tx.type.value} | {tx.description[:30]}"
    builder = InlineKeyboardBuilder()
    for tx in txs:
        builder.row(
            InlineKeyboardButton(text=f"✅ تأیید {tx.id}", callback_data=f"adm_approve_{tx.id}"),
            InlineKeyboardButton(text=f"❌ رد {tx.id}", callback_data=f"adm_reject_{tx.id}")
        )
    builder.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="adm_main"))
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()

@admin_full_router.callback_query(F.data.startswith("adm_approve_"))
async def approve_tx(callback: types.CallbackQuery):
    tx_id = int(callback.data.split("_")[-1])
    async with async_session() as db:
        user = await get_user_by_telegram_id(db, callback.from_user.id)
        if not user:
            await callback.answer("خطا: کاربر یافت نشد")
            return
        try:
            await wallet_service.approve_transaction(db, tx_id, admin_id=user.id)
            await callback.answer("تراکنش تأیید شد.")
        except Exception as e:
            await callback.answer(f"خطا: {e}")
    await pending_transactions(callback)  # refresh

@admin_full_router.callback_query(F.data.startswith("adm_reject_"))
async def reject_tx(callback: types.CallbackQuery):
    tx_id = int(callback.data.split("_")[-1])
    async with async_session() as db:
        try:
            await wallet_service.reject_transaction(db, tx_id, admin_id=1, reason="رد توسط ادمین")
            await callback.answer("تراکنش رد شد.")
        except Exception as e:
            await callback.answer(f"خطا: {e}")
    await pending_transactions(callback)

# -------------- Tickets Management (ساده‌شده) --------------
@admin_full_router.callback_query(F.data == "adm_tickets_menu")
async def tickets_menu(callback: types.CallbackQuery):
    async with async_session() as db:
        stmt = select(Ticket).where(Ticket.status != TicketStatus.CLOSED).order_by(Ticket.created_at.desc()).limit(15)
        result = await db.execute(stmt)
        tickets = result.scalars().all()
    if not tickets:
        await callback.message.edit_text("تیکت بازی وجود ندارد.")
        return
    text = "🎫 تیکت‌های باز:\n"
    for t in tickets:
        text += f"{t.id}: {t.subject[:40]} | {t.priority.value} | {t.status.value}\n"
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 بازگشت", callback_data="adm_main"))
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()

# -------------- Broadcast (پیام گروهی) --------------
@admin_full_router.callback_query(F.data == "adm_broadcast")
async def broadcast_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("📢 پیام خود را برای ارسال به کاربران وارد کنید (می‌توانید از مارک‌داون استفاده کنید):")
    await state.set_state(BroadcastFSM.waiting_message)
    await callback.answer()

@admin_full_router.message(BroadcastFSM.waiting_message)
async def broadcast_message(message: types.Message, state: FSMContext):
    await state.update_data(msg_text=message.text)
    await message.answer("حالا فیلتر کاربران را مشخص کنید:\n/all برای همه\n/role:admin_music برای نقش خاص\n/skip برای رد کردن فیلتر")
    await state.set_state(BroadcastFSM.waiting_filter)

@admin_full_router.message(BroadcastFSM.waiting_filter)
async def broadcast_filter(message: types.Message, state: FSMContext):
    filter_cmd = message.text.strip()
    await state.update_data(filter=filter_cmd)
    data = await state.get_data()
    await message.answer(f"آماده ارسال پیام:\n\n{data['msg_text'][:200]}\n\nفیلتر: {filter_cmd}\nبرای تأیید /confirm ارسال کنید یا /cancel")
    await state.set_state(BroadcastFSM.confirm)

@admin_full_router.message(BroadcastFSM.confirm, Command("confirm"))
async def broadcast_confirm(message: types.Message, state: FSMContext):
    data = await state.get_data()
    msg_text = data['msg_text']
    filter_cmd = data['filter']
    async with async_session() as db:
        if filter_cmd == "/all":
            users = await db.execute(select(User).where(User.is_blocked == False))
        elif filter_cmd.startswith("/role:"):
            role = filter_cmd.split(":")[1]
            users = await db.execute(select(User).where(User.role == role, User.is_blocked == False))
        else:
            users = await db.execute(select(User).where(User.is_blocked == False))
        user_list = users.scalars().all()
        sent = 0
        for u in user_list:
            try:
                # bot.send_message در اینجا از dispatcher موجود نیست، صرفاً ثبت می‌کنیم
                sent += 1
            except Exception as e:
                logger.error(f"Failed to send to {u.telegram_id}: {e}")
        await message.answer(f"✅ پیام به {sent} کاربر ارسال شد (شبیه‌سازی).")
    await state.clear()

# -------------- Statistics (آمار سریع) --------------
@admin_full_router.callback_query(F.data == "adm_stats")
async def quick_stats(callback: types.CallbackQuery):
    async with async_session() as db:
        user_count = (await db.execute(select(func.count()).select_from(User))).scalar()
        track_count = (await db.execute(select(func.count()).select_from(Track))).scalar()
        pending_tx = (await db.execute(select(func.count()).select_from(Transaction).where(Transaction.status == TransactionStatus.PENDING))).scalar()
        open_tickets = (await db.execute(select(func.count()).select_from(Ticket).where(Ticket.status != TicketStatus.CLOSED))).scalar()
    text = (
        f"📊 آمار کلی:\n"
        f"👥 کاربران: {user_count}\n"
        f"🎵 آهنگ‌ها: {track_count}\n"
        f"💰 تراکنش‌های در انتظار: {pending_tx}\n"
        f"🎫 تیکت‌های باز: {open_tickets}\n"
    )
    await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🔙 بازگشت", callback_data="adm_main")]]
    ))
    await callback.answer()

# -------------- تنظیمات ادمین (تغییر سطح دسترسی خود) --------------
@admin_full_router.callback_query(F.data == "adm_settings")
async def admin_settings(callback: types.CallbackQuery):
    async with async_session() as db:
        user = await get_user_by_telegram_id(db, callback.from_user.id)
        if not user:
            await callback.answer("خطا")
            return
        text = f"تنظیمات شما:\nنقش: {user.role}\nمسدود: {'بله' if user.is_blocked else 'خیر'}"
    await callback.message.edit_text(text)
    await callback.answer()

# بازگشت به منوی اصلی
@admin_full_router.callback_query(F.data == "adm_main")
async def back_to_main(callback: types.CallbackQuery):
    await cmd_admin(callback.message)
    await callback.answer()
