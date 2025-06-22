from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from handlers.states import RuUserReg
from config import SUPPORT_GROUP_ID
from aiogram.fsm.context import FSMContext
from keyboards import ru_keyboards as kb

from database.crud import get_or_create_user, create_transaction

from database.models import User
from database.models import Transaction


import re
import random

from aiogram.exceptions import TelegramBadRequest

router = Router()


#### Russian Version

@router.callback_query(F.data == 'russian')
async def russian_answer(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer('')
    user = callback.from_user
    await callback.message.answer_photo(
        photo='https://i.ibb.co/hRN3HhFz/photo-2025-06-22-15-43-52.jpg', 
        caption=f'{user.first_name} добро пожаловать в Paybet! 🎉 \n\nПополняй и выводи со счёта 1x БЕСПЛАТНО!💸✨', 
        reply_markup = kb.ru_options)


# Обработка вывода

@router.callback_query(F.data == 'ru_withdraw')
async def russian_withdraw_answer(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()

    await state.update_data(tg_id=callback.from_user.id)
    await state.update_data(type='withdraw')
    
    await callback.message.answer("📞 Пожалуйста, отправьте ваш номер телефона:", reply_markup=kb.ru_phone_number_kb)

    await state.set_state(RuUserReg.phone)

# Обработка депозита

@router.callback_query(F.data == 'ru_deposit')
async def russian_deposit_answer(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()

    await state.update_data(tg_id=callback.from_user.id)
    await state.update_data(type='deposit')
    
    await callback.message.answer("📞 Пожалуйста, отправьте ваш номер телефона:", reply_markup=kb.ru_phone_number_kb)

    await state.set_state(RuUserReg.phone)
    

@router.message(RuUserReg.phone)
async def process_contact(message: Message, state: FSMContext):
    if not message.contact:
        await message.answer("❗️ Пожалуйста, отправьте номер с помощью кнопки")
        return

    phone_number = message.contact.phone_number

    await state.update_data(phone=phone_number)

    await message.answer(f"✅ Номер принят: `{phone_number}`", parse_mode="Markdown", reply_markup=kb.ReplyKeyboardRemove())

    await message.answer_photo(
        photo='https://i.ibb.co/vCGYXGhj/photo-2025-06-20-12-45-23.jpg', 
        caption='Введите ваш ID ⬇️'
    )
    await state.set_state(RuUserReg.x_id)



@router.message(RuUserReg.x_id)
async def process_x_id(message: Message, state: FSMContext):

    platform_id = message.text.strip()

    if not platform_id.isdigit() or not (7 <= len(platform_id) <= 12):
        await message.answer("❌ Пожалуйста, введите ID только цифрами (от 7 до 12 символов)")
        return

    await state.update_data(x_id=platform_id)

    await message.answer(f"✅ ID принят: `{platform_id}`", parse_mode="Markdown")

    await message.answer(
        "💸 Введите сумму пополнения:\n\n"
        "🔹 *Мин.: 30 000 сум*\n"
        "🔹 *Макс.: 30 000 000 сум*\n\n"
        "🔸 Пример: `156000` (только цифры, без пробелов)",
        parse_mode="Markdown"
    )

    await state.set_state(RuUserReg.amount)

@router.message(RuUserReg.amount)
async def process_amount(message: Message, state: FSMContext):
    raw_text = message.text.replace(" ", "").strip()

    data = await state.get_data()
    tg_id = message.from_user.id
    phone = str(data.get("phone", "Не указана"))

    await get_or_create_user(tg_id=tg_id, phone=phone)

 
    if not raw_text.isdigit():
        await message.answer("❌ Используйте только цифры. Пример: `156000`", parse_mode="Markdown")
        return

    amount = int(raw_text)
    if not (30_000 <= amount <= 30_000_000):
        await message.answer("❌ Сумма должна быть от 30 000 до 30 000 000 сум")
        return

    await state.update_data(amount=amount)
    await message.answer(f"✅ Сумма принята: `{amount}` сум", parse_mode="Markdown")
    await message.answer(
        "💳 Теперь введите номер карты (16 цифр):\n\nПример:\n`1234 5678 9012 3456`\nИли\n`1234567890123456`",
        parse_mode="Markdown"
    )
    await state.set_state(RuUserReg.card_number)


async def show_summary(message: Message, state: FSMContext):
    data = await state.get_data()
    payment_number = random.randint(1000000000, 9999999999)

    x_id = data.get("x_id", "Не указан")
    amount = data.get("amount", "Не указана")
    card = data.get("card", "Не указана" )

    full_text = (
        f"♻️ *ID Заявки: {payment_number}*\n"
        f"💳 *Ваша карта: {card}*\n"
        f"🆔 *Ваш 1X ID: {x_id}*\n"
        f"💸 *Сумма: {amount} сум*\n\n"
        )
    
    if data['type'] == 'deposit':
        full_text += (
        f"❗️ *Переведите на карту* 👇\n"
        f"~~~~ `9860180110103520` ~~~~\n"
        )
        full_text += "\n\n⌛️ *Статус*: Ожидает оплаты..."
        keyboard = kb.ru_payment_kb

    if data['type'] == 'withdraw':
        full_text += f"\n✅ Код подтверждения: {data['confirm_code']}"
        full_text += "\n\n⌛️ *Статус*: Ожидает проверки..."
        keyboard = kb.ru_withdraw_kb

    await message.answer(full_text,
        parse_mode = "Markdown",
        reply_markup = keyboard
    )


@router.message(RuUserReg.card_number)
async def process_card_number(message: Message, state: FSMContext):
    raw = message.text.strip()
    digits_only = raw.replace(" ", "")

    if not digits_only.isdigit() or len(digits_only) != 16:
        await message.answer("❌ Номер карты должен содержать 16 цифр")
        return

    if not (re.fullmatch(r"\d{16}", raw) or re.fullmatch(r"(\d{4} ){3}\d{4}", raw)):
        await message.answer("❌ Пожалуйста, введите карту в формате:\n`1234 5678 9012 3456` или `1234567890123456`", parse_mode="Markdown")
        return

    await state.update_data(card=digits_only)
    data = await state.get_data()

    if data['type'] == 'withdraw':
        await state.set_state(RuUserReg.confirm_code)
        await message.answer_photo(photo="https://i.ibb.co/W47HRyCM/photo-2025-06-21-17-00-51.jpg", caption="Введите код подтверждения вывода")
    else:
        await state.set_state(RuUserReg.summary)
        await show_summary(message, state)


@router.message(RuUserReg.confirm_code)
async def confirm_code(message: Message, state: FSMContext):
    code = message.text.strip()

    if not re.fullmatch(r'[A-Za-z0-9]{4}', code):
        await message.answer("❌ Код должен содержать ровно 4 символа: буквы и/или цифры (например: dX6M). Попробуйте снова.")
        return

    await state.update_data(confirm_code=code)
    await state.set_state(RuUserReg.summary)
    await show_summary(message, state)



@router.callback_query(F.data == "ru_withdraw_done")
async def confirm_withdraw(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    card = data.get("card", "Не указана")
    x_id = data.get("x_id", "Не указан")
    amount = data.get("amount", "Не указана")
    phone = str(data.get("phone", "Не указана"))
    user_id = data.get("tg_id")
    confirmation_code = data.get('confirm_code')
    type = data.get("type", "Не указана")

    user = await get_or_create_user(tg_id = user_id, phone=phone)
    await create_transaction(user, amount=amount, x_id = x_id,  tx_type=type, verification_code=confirmation_code, card_number=card)
        
    payment_number = random.randint(1000000000, 9999999999)
    masked_card = f"{card}"

    await callback.message.answer(
        f"✅ Заявка принята\n\n"
        f"♻️ Платеж ID:  {payment_number}\n"
        f"💳 Карта: `{masked_card}`\n"
        f"🆔 1X ID: `{x_id}`\n"
        f"✅ Код подтверждения: `{confirmation_code}`\n"
        f"💵 Сумма: `{amount}` сум\n\n"
        f"⌛️ Статус: На проверке оператором...",
        reply_markup=kb.ReplyKeyboardRemove(), parse_mode = "Markdown"
    )

    await callback.bot.send_message(
        chat_id=SUPPORT_GROUP_ID,
        text=f"🆕 Новый вывод!\n\n"
             f"💳 Карта: `{masked_card}`\n"
             f"🆔 1X ID: `{x_id}`\n"
             f"✅ Код подтверждения: `{confirmation_code}`\n"
             f"💵 Сумма: `{amount}` сум\n"
             f"🔰 ID: {payment_number}\n\n"
             f"👤 Пользователь: {phone} / {user_id}",
        parse_mode="Markdown",
        reply_markup=kb.ru_get_confirmation_kb(payment_number, user_id)
    )
    await callback.answer()


@router.callback_query(F.data == "ru_payment_done")
async def confirm_payment(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    data = await state.get_data()
    card = data.get("card", "Не указана")
    x_id = data.get("x_id", "Не указан")
    amount = data.get("amount", "Не указана")
    phone = str(data.get("phone", "Не указана"))
    user_id = data.get("tg_id")
    confirmation_code = data.get('confirm_code', "Не указана")
    type = data.get("type", "Не указана")

    user = await get_or_create_user(user_id, phone=phone)
    await create_transaction(user, amount=amount, x_id = x_id,  tx_type=type, verification_code=confirmation_code, card_number=card)

    payment_number = random.randint(1000000000, 9999999999)
    masked_card = f"{card}"

    await callback.message.answer(
        f"♻️ Платеж ID:  {payment_number}\n"
        f"💳 Карта: `{masked_card}`\n"
        f"⌛️ Статус: На проверке оператором...",
        reply_markup=kb.ru_support, parse_mode="Markdown"
    )

    await callback.bot.send_message(
        chat_id=SUPPORT_GROUP_ID,
        text=f"🆕 Новый платеж!\n\n"
             f"💳 Карта: `{masked_card}`\n"
             f"🆔 1X ID: `{x_id}`\n"
             f"💵 Сумма: `{amount}` сум\n"
             f"🔰 ID: {payment_number}\n\n"
             f"👤 Пользователь: {phone} / {user_id}",
        parse_mode="Markdown",
        reply_markup=kb.ru_get_confirmation_kb(payment_number, user_id)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("ruconfirm_"))
async def admin_confirm_payment(callback: CallbackQuery, state: FSMContext):
    try:
        _, payment_number, user_id = callback.data.split('_')
        try:
            await callback.bot.send_message(
                chat_id=int(user_id),
                text=f"✅ Ваша заявка #{payment_number} выполнена, проверьте баланс!"
            )
            
            await callback.message.edit_text(
                text=f"{callback.message.text}\n\n✅ **Подтвержден**",
                parse_mode="Markdown"
            )
            
            await callback.answer("Платеж подтвержден!", show_alert=True)
            
            user = await User.get(tg_id=user_id)
            tx = await Transaction.filter(user=user).order_by('-created_at').first()
            tx.status = "Оплачено"
            await tx.save()

        except TelegramBadRequest as e:
            if "chat not found" in str(e):
                await callback.message.edit_text(
                    text=f"{callback.message.text}\n\n❌ Пользователь не найден (заблокировал бота?)",
                    parse_mode="Markdown"
                )
            else:
                await callback.answer(f"❌ Ошибка: {e}", show_alert=True)
                raise

    except Exception as e:
        await callback.answer(f"❌ Ошибка системы: {e}", show_alert=True)
        raise


@router.callback_query(F.data == "go_home")
async def back_to_main(callback: CallbackQuery):
    try:
        await callback.message.delete()
        

        await callback.message.answer(
            text='Выберите язык / Tilni tanlang 👇',
            reply_markup=kb.settings
        )
        
        await callback.answer()
        
    except Exception as e:
        await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)   