from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder



uz_back = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔙 Ortga")],
    ],
    resize_keyboard=True  
)

uz_options = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💰 Hisobni to‘ldirish", callback_data='uz_deposit')],
    [InlineKeyboardButton(text="📤 Pul yechish", callback_data='uz_withdraw')],
    [InlineKeyboardButton(text="💬 Yordam", url='https://t.me/NU220897')]
])

uz_phone_number_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📲 Raqamni yuborish", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

uz_inline_back = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙 Ortga", callback_data="uzbek")]
])


uz_payment_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ To'ladim", callback_data="uz_payment_done")],
    [InlineKeyboardButton(text="💬 Yordam", url='https://t.me/NU220897')],
    [InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="uzbek")]
])

uz_withdraw_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Hammasi to'gri", callback_data="uz_withdraw_done")],
    [InlineKeyboardButton(text="🔙 Bosh menu", callback_data="uzbek")]
])


def get_confirmation_kb(payment_number: int, user_id: int, x_id: int, transaction_type: str, confirm_code: str = "None"):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Tasdiqlash", 
        callback_data=f"confirm_{payment_number}_{user_id}_{x_id}_{transaction_type}_{confirm_code}"
    )
    return builder.as_markup()

uz_support = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💬 Yordam", url='https://t.me/NU220897')],
    [InlineKeyboardButton(text="🔙 Bosh menu", callback_data="uzbek")]
])