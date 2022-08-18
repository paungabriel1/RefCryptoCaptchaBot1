from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import *


### ---___--- ЮЗЕР МЕНЮ ---___--- ###
async def main_menu_keyboard():
    if language == "RUS":
        send_gift = InlineKeyboardButton(text="🎁 Отправить подарок", switch_inline_query="")
        update_balance = InlineKeyboardButton(text="🔄 Обновить баланс", callback_data="update_balance")
        withdraw_funds = InlineKeyboardButton(text="📥 Вывод средств", callback_data="withdraw_funds")
    elif language == "ENG":
        send_gift = InlineKeyboardButton(text="🎁 Send a gift", switch_inline_query="")
        update_balance = InlineKeyboardButton(text="🔄 Update your balance", callback_data="update_balance")
        withdraw_funds = InlineKeyboardButton(text="📥 Withdrawal of funds", callback_data="withdraw_funds")

    main_menu = InlineKeyboardMarkup(row_width=2).add(update_balance, withdraw_funds, send_gift)
    return main_menu


async def get_gift_menu_keyboard(username_bot, tg_id):
    if language == "RUS":
        get_gift = InlineKeyboardButton(text="🎁 Получить подарок", url=f"https://t.me/{username_bot}?start={tg_id}")
    elif language == "ENG":
        get_gift = InlineKeyboardButton(text="🎁 Get a gift", url=f"https://t.me/{username_bot}?start={tg_id}")
    get_gift_menu = InlineKeyboardMarkup().add(get_gift)
    return get_gift_menu


async def update_follow_menu_keyboard():
    if language == "RUS":
        update_follow = InlineKeyboardButton(text="🔍 Проверить подписку", callback_data="update_follow")
    elif language == "ENG":
        update_follow = InlineKeyboardButton(text="🔍 Check your subscription", callback_data="update_follow")
    update_follow_menu = InlineKeyboardMarkup(row_width=1).add(update_follow)
    return update_follow_menu


### ---___--- АДМИН МЕНЮ ---___--- ###
async def admin_menu_keyboard():
    number_users = InlineKeyboardButton(text="👥 Количество пользователей", callback_data="number_users")
    download_database = InlineKeyboardButton(text="⏬ Скачать базу данных", callback_data="download_database")
    private_message = InlineKeyboardButton(text="✉ Личное сообщение", callback_data="private_message")
    mailing = InlineKeyboardButton(text="📪 Массовая рассылка", callback_data="mailing")
    changing_balance = InlineKeyboardButton(text="💰 Изменение баланса", callback_data="changing_balance")
    deleted_message = InlineKeyboardButton(text="❌ Закрыть сообщение", callback_data="deleted_message")
    admin_menu = InlineKeyboardMarkup(row_width=2).add(number_users, download_database, private_message, mailing,
                                                       changing_balance, deleted_message)
    return admin_menu


async def info_menu_keyboard():
    update_info = InlineKeyboardButton(text="🔄 Обновить", callback_data="update_info")
    deleted_message = InlineKeyboardButton(text="❌ Закрыть сообщение", callback_data="deleted_message")
    info_menu = InlineKeyboardMarkup(row_width=1).add(update_info, deleted_message)
    return info_menu


### ---___--- ОБЩЕЕ МЕНЮ ---___--- ###
async def deleted_message_menu_keyboard():
    if language == "RUS":
        deleted_message = InlineKeyboardButton(text="❌ Закрыть сообщение", callback_data="deleted_message")
    elif language == "ENG":
        deleted_message = InlineKeyboardButton(text="❌ Сlose the message", callback_data="deleted_message")
    deleted_message_menu = InlineKeyboardMarkup(row_width=1).add(deleted_message)
    return deleted_message_menu

