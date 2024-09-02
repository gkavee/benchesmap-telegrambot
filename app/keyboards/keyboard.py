from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

"""
Replies
"""
main = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🔍Найти лавочку"),
            KeyboardButton(text="➕Создать лавочку"),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="???",
)

geo = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отправить геолокацию", request_location=True)],
        [KeyboardButton(text="Отмена❌")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Отправьте геолокацию",
)

cancel = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Отмена❌")]], resize_keyboard=True
)

reply_rm = ReplyKeyboardRemove()

"""
Inlines
"""
del_or_edit_bench = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌Удалить лавочку", callback_data="delete_bench")],
        [
            InlineKeyboardButton(
                text="✏️Редактировать лавочку", callback_data="edit_bench_open"
            )
        ],
    ]
)

edit_bench = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Название", callback_data="edit_bench_name"),
            InlineKeyboardButton(
                text="Описание", callback_data="edit_bench_description"
            ),
        ],
        [
            InlineKeyboardButton(text="Количество", callback_data="edit_bench_count"),
            InlineKeyboardButton(
                text="Геолокацию", callback_data="edit_bench_location"
            ),
        ],
        [InlineKeyboardButton(text="⬅️Назад", callback_data="edit_bench_cancel")],
    ]
)
