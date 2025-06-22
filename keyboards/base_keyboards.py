from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


settings = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Русский 🇷🇺', callback_data='russian'), InlineKeyboardButton(text="O'zbekcha 🇺🇿", callback_data='uzbek')]
                                                ])