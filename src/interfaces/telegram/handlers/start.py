from aiogram import Router, types
from aiogram.filters import CommandStart

start_router = Router()

@start_router.message(CommandStart())
async def start_command(message: types.Message):
    # در آینده از منوی ساخته‌شده در پنل (دیتابیس) خوانده شود
    await message.answer("به TEOS خوش آمدید. لطفاً گزینه مورد نظر را انتخاب کنید.", reply_markup=types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🎵 موزیک")],
            [types.KeyboardButton(text="🛠 سرویس‌ها")],
            [types.KeyboardButton(text="💰 کیف پول")],
            [types.KeyboardButton(text="🎧 پشتیبانی")]
        ],
        resize_keyboard=True
    ))
