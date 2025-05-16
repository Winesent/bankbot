from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup

def main_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="💰 Баланс")
    builder.button(text="💸 Перевести")
    if is_admin:
        builder.button(text="👑 Админ-панель")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def admin_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="Начислить")
    builder.button(text="Списать")
    builder.button(text="Проверить баланс")
    builder.button(text="◀️ Назад")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def cancel_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="❌ Отмена")
    return builder.as_markup(resize_keyboard=True)