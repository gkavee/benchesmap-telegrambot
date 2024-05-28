from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton

'''
Replies
'''
main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='🔍Найти лавочку'), KeyboardButton(text='➕Создать лавочку')],
], resize_keyboard=True, input_field_placeholder="???")

geo = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Отправить геолокацию', request_location=True)],
    [KeyboardButton(text='Отмена❌')]
], resize_keyboard=True, input_field_placeholder="Отправьте геолокацию")

cancel = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Отмена❌')]], resize_keyboard=True)

reply_rm = ReplyKeyboardRemove()

'''
Inlines
'''
bench_delete = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="/delete", url='https://t.me/sdfsdf890')
        ]
    ]
)
