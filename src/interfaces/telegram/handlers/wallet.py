from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import async_session
from src.modules.wallet_payment.service import wallet_service

wallet_router = Router()

class DepositStates(StatesGroup):
    waiting_for_amount = State()
    waiting_for_receipt = State()

@wallet_router.callback_query(F.data == "wallet_menu")
async def wallet_menu(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    async with async_session() as db:
        from src.core.user_engine import get_user_by_telegram_id
        user = await get_user_by_telegram_id(db, user_id)
        wallet = await wallet_service.get_wallet_by_user(db, user.id) if user else None
        balance = wallet.balance if wallet else 0.0
    text = f"💰 کیف پول\n\nموجودی: {balance:,} تومان"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💸 شارژ کیف پول", callback_data="wallet_deposit")],
        [InlineKeyboardButton(text="📊 تاریخچه تراکنش‌ها", callback_data="wallet_history")],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="main_menu")]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@wallet_router.callback_query(F.data == "wallet_deposit")
async def deposit_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("لطفاً مبلغ مورد نظر را به تومان وارد کنید (عدد):")
    await state.set_state(DepositStates.waiting_for_amount)
    await callback.answer()

@wallet_router.message(DepositStates.waiting_for_amount)
async def deposit_amount(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text)
        if amount <= 0:
            raise ValueError
    except:
        await message.answer("مبلغ نامعتبر است. یک عدد مثبت وارد کنید.")
        return
    await state.update_data(amount=amount)
    await message.answer("حالا تصویر رسید پرداخت را ارسال کنید.")
    await state.set_state(DepositStates.waiting_for_receipt)

@wallet_router.message(DepositStates.waiting_for_receipt, F.photo)
async def deposit_receipt(message: types.Message, state: FSMContext):
    data = await state.get_data()
    amount = data['amount']
    user_id = message.from_user.id
    # گرفتن file_id عکس
    file_id = message.photo[-1].file_id
    async with async_session() as db:
        from src.core.user_engine import get_user_by_telegram_id
        user = await get_user_by_telegram_id(db, user_id)
        if not user:
            await message.answer("خطا: کاربر یافت نشد.")
            return
        try:
            transaction = await wallet_service.deposit_request(db, user.id, amount, "شارژ حساب", file_id)
            await message.answer(f"درخواست شارژ {amount} تومان ثبت شد.\nکد پیگیری: {transaction.id}\nدر انتظار تأیید ادمین.")
        except Exception as e:
            await message.answer(f"خطا در ثبت: {str(e)}")
    await state.clear()
