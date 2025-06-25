from aiogram import F, Router, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from keyboards import base_keyboards as kb
from google_sheets_client.gshits_client import export_to_google_sheets
from config import ADMIN_IDS

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message
    await message.answer('Выберите язык / Tilni tanlang 👇', 
        reply_markup = kb.settings)
    

@router.message(F.text == "/export")
async def handle_export(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return await message.answer("⛔ У вас нет доступа к этой команде.")

    await message.answer("⏳ Экспорт данных в Google Sheets начался...")
    try:
        await export_to_google_sheets()
        await message.answer("✅ Экспорт завершён успешно.")
    except Exception as e:
        await message.answer(f"❌ Ошибка при экспорте: {e}")