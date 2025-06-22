from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from keyboards import base_keyboards as kb

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message
    await message.answer('Выберите язык / Tilni tanlang 👇', 
        reply_markup = kb.settings)