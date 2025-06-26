from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from handlers.states import UzUserReg
from aiogram.exceptions import TelegramBadRequest

#KEYBORDS
from keyboards import uz_keyboards as kb

#DATABASE
from database.crud import get_or_create_user, create_transaction
from database.models import User
from database.models import Transaction

#UTILS
import re
import random
import os
from dotenv import load_dotenv

#CLIENT
from clients.api_client import AsyncCashdeskBotClient


load_dotenv()
router = Router()

SUPPORT_GROUP_ID = os.getenv("SUPPORT_GROUP_ID")

#### Uzbek version

@router.callback_query(F.data == 'uzbek')
async def uzbek_answer(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer('')
    user = callback.from_user
    await callback.message.answer_photo(
        photo='https://i.ibb.co/hRN3HhFz/photo-2025-06-22-15-43-52.jpg', 
        caption=f'{user.first_name} Paybet’ga xush kelibsiz! 🎉 \n\n1x hisobingizni BEPUL to‘ldiring va yeching! 💸✨', 
        reply_markup = kb.uz_options)


# Обработка вывода

@router.callback_query(F.data == 'uz_withdraw')
async def uzbek_withdraw_answer(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()

    await state.update_data(tg_id=callback.from_user.id)
    await state.update_data(type='withdraw')
    
    user_id = callback.from_user.id
    user = await User.get_or_none(tg_id=int(user_id))

    if not user:
        await callback.message.answer("📞 Iltimos, telefon raqamingizni yuboring:", reply_markup= kb.uz_phone_number_kb)

        await state.set_state(UzUserReg.phone)
    else:
        await state.update_data(phone=user.phone_number)
        await callback.message.answer_photo(
        photo='https://i.ibb.co/vCGYXGhj/photo-2025-06-20-12-45-23.jpg', 
        caption='ID raqamni kiriting ⬇️'
    )
        await state.set_state(UzUserReg.x_id)


# Обработка депозита

@router.callback_query(F.data == 'uz_deposit')
async def uzbek_deposit_answer(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()

    await state.update_data(tg_id=callback.from_user.id)
    await state.update_data(type='deposit')
    
    user_id = callback.from_user.id
    user = await User.get_or_none(tg_id=int(user_id))

    if not user:
        await callback.message.answer("📞 Iltimos, telefon raqamingizni yuboring:", reply_markup= kb.uz_phone_number_kb)

        await state.set_state(UzUserReg.phone)
    else:
        await state.update_data(phone=user.phone_number)
        await callback.message.answer_photo(
        photo='https://i.ibb.co/vCGYXGhj/photo-2025-06-20-12-45-23.jpg', 
        caption='ID raqamni kiriting ⬇️'
    )
        await state.set_state(UzUserReg.x_id)
    

@router.message(UzUserReg.phone)
async def process_contact(message: Message, state: FSMContext):
    if not message.contact:
        await message.answer("❗️ Iltimos, tugmani bosib raqamni yuboring.")
        return

    phone_number = message.contact.phone_number

    await state.update_data(phone=phone_number)

    await message.answer(f"✅ Raqam qabul qilindi: {phone_number}", parse_mode="Markdown", reply_markup= kb.ReplyKeyboardRemove())

    await message.answer_photo(
        photo='https://i.ibb.co/vCGYXGhj/photo-2025-06-20-12-45-23.jpg', 
        caption='ID raqamni kiriting ⬇️'
    )
    await state.set_state(UzUserReg.x_id)


@router.message(UzUserReg.x_id)
async def process_x_id(message: Message, state: FSMContext):

    platform_id = message.text.strip()

    if not platform_id.isdigit() or not (7 <= len(platform_id) <= 12):
        await message.answer("❌ Iltimos, faqat 7 dan 12 gacha raqamlardan iborat ID kiriting.")
        return
    
    try:
        async with AsyncCashdeskBotClient() as client:
            if not await client.player_exists(platform_id):
                await message.answer(f"❌ ID {platform_id}  mavjud emas, qayta tekshirib to'gri kiriting")
                return
    except Exception:
        await message.answer("⚠️ Tekshirish xatosi. Keyinroq harakat qilib ko'ring")
        return
    
    await state.update_data(x_id=platform_id)


    try:
        async with AsyncCashdeskBotClient() as client:
                name = await client.player_exists(platform_id)
                await state.update_data(name=name['Name'])

        await message.answer(f"🔹 {name['Name']}   \n✅ ID qabul qilindi: {platform_id}", parse_mode="Markdown")

    except:
        await message.answer("⚠️ Tekshirish xatosi. Keyinroq harakat qilib ko'ring")
        return

    data = await state.get_data()
    

    if data["type"] == "deposit":
        await message.answer(
            "💸 Hisobni to‘ldirish summasini kiriting:\n\n"
            "🔹 *Eng kam: 30 000 so‘m*\n"
            "🔹 *Eng ko‘p: 30 000 000 so‘m*\n\n"
            "🔸 Misol: 156000 (faqat raqamlar, bo‘shliqsiz)",
            parse_mode="Markdown"
        )

        await state.set_state(UzUserReg.amount)
    else:
        await message.answer(
        "💳 Endi karta raqamini kiriting (16 ta raqam):\n\nMisol:\n`1234 5678 9012 3456`\nYoki\n`1234567890123456`",
        parse_mode="Markdown"
    )
        await state.set_state(UzUserReg.card_number)



@router.message(UzUserReg.amount)
async def process_amount(message: Message, state: FSMContext):
    raw_text = message.text.replace(" ", "").strip()

    data = await state.get_data()
    tg_id = message.from_user.id
    phone = str(data.get("phone", "Не указана"))

    await get_or_create_user(tg_id=tg_id, phone=phone)


    if not raw_text.isdigit():
        await message.answer("❌ Faqat raqamlardan foydalaning. Misol: `156000`", parse_mode="Markdown")
        return

    await get_or_create_user(tg_id, phone=phone)

    amount = int(raw_text)
    if not (30_000 <= amount <= 30_000_000):
        await message.answer("❌ Miqdor 30 000 so'mdan kam yoki 30 000 000 so'mdan katta bo‘lishi mumkin emas.")
        return

    total_with_fee = round(amount + random.randint(10, 99))
    await state.update_data(actual_amount=amount)
    await state.update_data(amount=total_with_fee)

    await message.answer(f"✅ Miqdor qabul qilindi")


    await message.answer(
        "💳 Endi karta raqamingizni yuboring (faqat 16 raqam):\n\nMisol:\n`1234 5678 9012 3456`\nYoki\n`1234567890123456`",
        parse_mode="Markdown"
    )
    await state.set_state(UzUserReg.card_number)


async def show_summary(message: Message, state: FSMContext):
    data = await state.get_data()
    x_id = data.get("x_id", "Не указан")
    amount = data.get("amount", "Не указана")
    card = data.get("card", "Не указана" )
    name = str(data.get("name", "Не указана"))
    actual_amount = data.get("actual_amount", "Не указана")
    user_id = data.get("tg_id")

    user = await User.get(tg_id=user_id)
    tx = await Transaction.filter(user=user).order_by('-created_at').first()

    full_text = (
        f"🙋 *{name}\n*"
        f"💳 *Sizning kartangiz: {card}*\n"
        f"🆔 *Sizning 1X ID: {x_id}*\n"
        )
    
    if data['type'] == 'deposit':
        full_text += (
        f"\n❌️ *Summa:* ~{actual_amount}~ *сум*\n"
        f"💸 *Summa: {amount} сум*\n\n"
        f"❗️ *Quyidagi kartaga pul yuboring* 👇\n"
        f"~~~~ `9860180110103520` ~~~~\n"
        )
        full_text += "\n\n⌛️ *Holat*: To‘lov kutilmoqda..."
        keyboard = kb.uz_payment_kb

    if data['type'] == 'withdraw':
        full_text += f"\n✅ Tasdiqlash kodi: {data['confirm_code']}"
        full_text += "\n\n✅ *Holat*: Pul mablag‘i karta hisobingizga 5 daqiqa ichida tushadi, javobni kuting!"
        keyboard = kb.uz_support
        await handle_withdraw_confirm(state, message.bot)
        
    await message.answer(full_text,
        parse_mode = "Markdown",
        reply_markup = keyboard
    )


@router.message(UzUserReg.card_number)
async def process_card_number(message: Message, state: FSMContext):
    raw = message.text.strip()
    digits_only = raw.replace(" ", "")

    if not digits_only.isdigit() or len(digits_only) != 16:
        await message.answer("❌ Karta faqat 16 ta raqamdan iborat bo‘lishi kerak.")
        return

    if not (re.fullmatch(r"\d{16}", raw) or re.fullmatch(r"(\d{4} ){3}\d{4}", raw)):
        await message.answer("❌ Iltimos, kartani quyidagi formatda kiriting:\n`1234 5678 9012 3456` yoki `1234567890123456`", parse_mode="Markdown")
        return

    await state.update_data(card=digits_only)
    data = await state.get_data()

    if data['type'] == 'withdraw':
        await state.set_state(UzUserReg.confirm_code)
        await message.answer_photo(photo="https://i.ibb.co/W47HRyCM/photo-2025-06-21-17-00-51.jpg", caption="Iltimos, tasdiqlash kodini kiriting")
    else:
        await state.set_state(UzUserReg.summary)
        await show_summary(message, state)


@router.message(UzUserReg.confirm_code)
async def confirm_code(message: Message, state: FSMContext):
    code = message.text.strip()
    data = await state.get_data()
    x_id = str(data["x_id"])

    if not re.fullmatch(r'[A-Za-z0-9]{4}', code):
        await message.answer("❌ Kodda aniq 4 ta belgi bo'lishi kerak: harflar va/yoki raqamlar (masalan: dX6M). Yana urinib ko'ring.")
        return

    async with AsyncCashdeskBotClient() as client:
        result = await client.withdraw(
                        user_id=x_id,
                        code=code
                    )
        
        if result.get('Success'):
            amount = int(result['Summa'])
            await state.update_data(amount=amount)
            await state.update_data(confirm_code=code)
            await state.set_state(UzUserReg.summary)
            await show_summary(message, state)
        else:
            await message.answer("❌ Noto‘g‘ri tasdiqlash kodi. Qaytadan urinib ko‘ring.")
            return

async def handle_withdraw_confirm(state: FSMContext, bot: Bot):
    data = await state.get_data()
    card = data.get("card", "Не указана")
    x_id = data.get("x_id", "Не указан")
    amount = data.get("amount", "Не указана")
    phone = str(data.get("phone", "Не указана"))
    user_id = data.get("tg_id")
    confirmation_code = data.get('confirm_code')
    tx_type = data.get("type", "Не указана")
    name = str(data.get("name", "Не указана"))

    user = await get_or_create_user(tg_id=user_id, phone=phone)
    tx_check = await create_transaction(user, amount=0, x_id=x_id, tx_type=tx_type,
                                        verification_code=confirmation_code, card_number=card)

    await bot.send_message(
        chat_id=SUPPORT_GROUP_ID,
        text=(
            f"🆕 Новый вывод!\n\n"
            f"🔰 ID: {tx_check.id}\n"
            f"🙋 *{name}\n*"
            f"💳 Карта: `{card}`\n"
            f"🆔 1X ID: `{x_id}`\n"
            f"✅ Код подтверждения: `{confirmation_code}`\n"
            f"💵 Сумма: `{amount}` сум\n"
            f"👤 Пользователь: +{phone}"
        ),
        parse_mode="Markdown",
        reply_markup=kb.ru_get_confirmation_kb(
            payment_number=tx_check.id,
            user_id=user_id,
            x_id=x_id,
            confirm_code=confirmation_code,
            transaction_type=tx_type
        )
    )

@router.callback_query(F.data == "uz_withdraw_done")
async def confirm_withdraw(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await handle_withdraw_confirm(state, callback.bot)
    await callback.answer()

# @router.callback_query(F.data == "uz_withdraw_done")
# async def confirm_withdraw(callback: CallbackQuery, state: FSMContext):
#     await callback.message.delete()  
#     data = await state.get_data()
#     card = data.get("card", "Не указана")
#     x_id = data.get("x_id", "Не указан")
#     amount = data.get("amount", "Не указана")
#     phone = str(data.get("phone", "Не указана"))
#     user_id = data.get("tg_id")
#     confirmation_code = data.get('confirm_code')
#     type = data.get("type", "Не указана")
#     name = str(data.get("name", "Не указана"))
#     user = await get_or_create_user(user_id, phone=phone)
#     tx_check = await create_transaction(user, amount=amount, x_id = x_id,  tx_type=type, verification_code=confirmation_code, card_number=card)
    
#     masked_card = f"{card}"

    
#     await callback.message.answer(
#         f"✅ *So‘rov qabul qilindi*\n\n"
#         f"♻️ *To‘lov ID:  {tx_check.id}*\n"
#         f"🙋 *{name}\n*"
#         f"💳 *Karta: {masked_card}*\n"
#         f"🆔 *1X ID: {x_id}*\n"
#         f"✅ *Tasdiqlash kodi: `{confirmation_code}`*\n"
#         f"⌛️ *Holat:* Operator tomonidan tekshirilmoqda...",
#         reply_markup=kb.uz_support, parse_mode="Markdown"
#     )

#     await callback.bot.send_message(
#         chat_id=SUPPORT_GROUP_ID,
#         text=f"🆕 Yangi yechib olish!\n\n"
#              f"🔰 ID: {tx_check.id}\n"
#              f"🙋 *{name}\n*"
#              f"💳 Karta: `{masked_card}`\n"
#              f"🆔 1X ID: `{x_id}`\n"
#              f"✅ Tasdiqlash kodi: `{confirmation_code}`\n"
#              f"💵 Summasi: `{amount}` so‘m\n"
#              f"👤 Foydalanuvchi: +{phone}",
#         parse_mode="Markdown",
#         reply_markup=kb.get_confirmation_kb(payment_number=tx_check.id, 
#         user_id=user_id, x_id=x_id, confirm_code=confirmation_code, transaction_type=type))
    
#     await callback.answer()



@router.callback_query(F.data == "uz_payment_done")
async def confirm_payment(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()       
    data = await state.get_data()
    card = data.get("card", "Не указана")
    x_id = data.get("x_id", "Не указан")
    amount = data.get("amount", "Не указана")
    phone = str(data.get("phone", "Не указана"))
    name = str(data.get("name", "Не указана"))
    user_id = data.get("tg_id")
    confirmation_code = data.get('confirm_code', "Не указана")
    type = data.get("type", "Не указана")

    user = await get_or_create_user(user_id, phone=phone)
    tx_check = await create_transaction(user, amount=amount, x_id = x_id,  tx_type=type, verification_code=confirmation_code, card_number=card)

    await callback.message.answer(
        f"✅ *Arizangiz qabul qilindi*\n\n"
        f"♻️ *To'lov ID: {tx_check.id}*\n"
        f"🙋 *{name}\n*"
        f"💳 *Karta: {card}*\n"
        f"💵 *Summasi: {amount} so'm*\n\n"
        f"⌛️ *Holat:* Operator tekshiruvi kutilmoqda...",
        reply_markup=kb.uz_support, parse_mode="Markdown"
    )
    

    await callback.bot.send_message(
        chat_id=SUPPORT_GROUP_ID,
        text=f"🆕 Yangi to'lov!\n\n"
             f"🔰 ID: {tx_check.id}\n"
             f"🙋 *{name}\n*"
             f"💳 Karta: `{card}`\n"
             f"🆔 1X ID: `{x_id}`\n"
             f"💵 Summa: `{amount}` so'm\n"
             f"👤 Foydalanuvchi: {phone}",
        parse_mode="Markdown",
        reply_markup=kb.get_confirmation_kb(payment_number=tx_check.id, 
        user_id=user_id, x_id=x_id, confirm_code=confirmation_code, transaction_type=type)
    )
    
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_"))
async def admin_confirm_payment(callback: CallbackQuery, state: FSMContext):

    try:
        _, payment_number, user_id, x_id, transaction_type, confirm_code = callback.data.split('_')
        user = await User.get(tg_id=user_id)
        tx = await Transaction.filter(user=user).order_by('-created_at').first()

        try:
            async with AsyncCashdeskBotClient() as client:
                if transaction_type == 'withdraw':
                    result = {'Success': True}
                else:
                    result = await client.deposit(
                        user_id=x_id,
                        amount=float(tx.amount)
                    )
                
                if result.get('Success'):                   
                    tx.status = "Оплачено"
                    await tx.save()
                    
                    await callback.bot.send_message(
                        chat_id=int(user_id),
                        text=f"✅ Sizning arizangiz #{payment_number} tasdiqlandi, balansingizni tekshiring!"
                    )
                    
                    await callback.message.edit_text(
                        text=f"{callback.message.text}\n\n✅ **Tasdiqlandi**",
                        parse_mode="Markdown"
                    )
                    await callback.answer("To'lov tasdiqlandi!", show_alert=True)
                else:
                    raise Exception("API request failed")
        
        except TelegramBadRequest as e:
            if "chat not found" in str(e):
                await callback.message.edit_text(
                    text=f"{callback.message.text}\n\n❌ Foydalanuvchi botni bloklagan",
                    parse_mode="Markdown"
                )
            else:
                raise
        except Exception as e:
            await callback.bot.send_message(
                chat_id=int(user_id),
                text=f"❌ Xatolik yuz berdi #{payment_number} keyinroq urinib ko'ring!"
            )
            raise
    
    except Exception as e:
        await callback.answer(f"❌ Xatolik: {e}", show_alert=True)
        raise


@router.callback_query(F.data == "go_home")
async def back_to_main(callback: CallbackQuery):
    try:        

        await callback.message.answer(
            text='Выберите язык / Tilni tanlang 👇',
            reply_markup=kb.settings
        )
        
        await callback.answer()
        
    except Exception as e:
        await callback.answer(f"❌ Xatolik: {str(e)}", show_alert=True)


