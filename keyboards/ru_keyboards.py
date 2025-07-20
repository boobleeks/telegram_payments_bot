from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


ru_back = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔙 Назад")],
    ],
    resize_keyboard=True  
)

ru_inline_back = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙 Назад", callback_data="russian")]
])

ru_options = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💰 Пополнить", callback_data='ru_deposit')],
    [InlineKeyboardButton(text="📤 Вывести", callback_data='ru_withdraw')],
    [InlineKeyboardButton(text="💬 Служба поддержки", url='https://t.me/NU220897')]
    ])

ru_phone_number_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📲 Отправить контакт", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

ru_payment_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Оплатил", callback_data="ru_payment_done")],
    [InlineKeyboardButton(text="💬 Служба поддержки", url='https://t.me/NU220897')],
    [InlineKeyboardButton(text="🔙 Главное Меню", callback_data="russian")]
])

ru_withdraw_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Всё верно", callback_data="ru_withdraw_done")],
    [InlineKeyboardButton(text="🔙 Главное Меню", callback_data="russian")]
])


def ru_get_confirmation_kb(payment_number: int, user_id: int, x_id: int, transaction_type: str, confirm_code: str = "None"):    
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Подтвердить", 
        callback_data=f"ruconfirm_{payment_number}_{user_id}_{x_id}_{transaction_type}_{confirm_code}"
    )
    return builder.as_markup()

ru_support = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💬 Служба поддержки", url='https://t.me/NU220897')],
    [InlineKeyboardButton(text="🔙 Главное Меню", callback_data="russian")]
])