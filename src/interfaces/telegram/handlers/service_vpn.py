from aiogram import Router, F, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import async_session
from src.modules.service_vpn.service import vpn_service, ServiceType

service_router = Router()

@service_router.callback_query(F.data == "menu_services")
async def show_services_menu(callback: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🌐 VPN", callback_data="service_list_vpn"))
    builder.row(types.InlineKeyboardButton(text="🖥 سرور", callback_data="service_list_server"))
    builder.row(types.InlineKeyboardButton(text="📊 وضعیت سفارش‌ها", callback_data="service_orders"))
    await callback.message.edit_text("🛠 بخش سرویس‌ها", reply_markup=builder.as_markup())
    await callback.answer()

@service_router.callback_query(F.data.startswith("service_list_"))
async def list_plans(callback: types.CallbackQuery):
    plan_type = callback.data.split("_")[-1]
    try:
        ptype = ServiceType(plan_type)
    except:
        ptype = None
    async with async_session() as db:
        plans = await vpn_service.get_active_plans(db, ptype)
    if not plans:
        await callback.message.answer("در حال حاضر پلنی موجود نیست.")
        return
    builder = InlineKeyboardBuilder()
    for plan in plans:
        builder.row(types.InlineKeyboardButton(
            text=f"{plan.name} - {plan.price} تومان",
            callback_data=f"service_plan_{plan.id}"
        ))
    builder.row(types.InlineKeyboardButton(text="🔙 بازگشت", callback_data="menu_services"))
    await callback.message.edit_text("پلن‌های موجود:", reply_markup=builder.as_markup())
    await callback.answer()

@service_router.callback_query(F.data.startswith("service_plan_"))
async def plan_detail(callback: types.CallbackQuery):
    plan_id = int(callback.data.split("_")[-1])
    async with async_session() as db:
        plan = await db.get(ServicePlan, plan_id)
    if not plan:
        await callback.answer("پلن یافت نشد")
        return
    text = f"📋 {plan.name}\n{plan.description or ''}\n💵 قیمت: {plan.price} تومان\n⏳ مدت: {plan.duration_days} روز\n📊 موجودی: {'نامحدود' if plan.stock == -1 else plan.stock}"
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="🛒 خرید با کیف پول", callback_data=f"buy_plan_{plan.id}_wallet"))
    builder.row(types.InlineKeyboardButton(text="💳 خرید مستقیم", callback_data=f"buy_plan_{plan.id}_direct"))
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()
