import asyncio
import datetime
import hashlib
import random
import string
import logging
import os

import httpx
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from claptcha import Claptcha

from classes import *
from database import *
from keyboard import *

bot = Bot(token=bot_api, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)

language = language.upper()

currency = currency.lower()
if currency == "usd":
    currency_sign = "$"
elif currency == "rub":
    currency_sign = "₽"

minimal_withdrawal_amount = Decimal(minimal_withdrawal_amount).quantize(Decimal("0.000001")).normalize()
amount_per_one = Decimal(amount_per_one).quantize(Decimal("0.000001")).normalize()


async def check_follow_channels(user_id):
    check_status = []
    id_channels = list(channels.values())
    for i in range(len(channels)):
        id_channel = id_channels[i]
        user_channels_status = await bot.get_chat_member(chat_id=id_channel, user_id=user_id)
        if user_channels_status["status"] == "left":
            check_status.append(False)
        else:
            check_status.append(True)
    if not False in check_status:
        return True


async def no_follow_message(user_id):
    unfollow_channels = '\n'.join(list(channels.keys()))
    if language == "RUS":
        await bot.send_message(user_id,
                               f"<b>Ваш друг отправил вам несколько монет {cryptocurrency}, чтобы получить их подпишитесь на каналы</b>\n\n"
                               f"<b>{unfollow_channels}</b>",
                               reply_markup=await update_follow_menu_keyboard())
    elif language == "ENG":
        await bot.send_message(user_id,
                               f"<b>Your friend sent you some coins {cryptocurrency}, to get them subscribe to the channels</b>\n\n"
                               f"<b>{unfollow_channels}</b>",
                               reply_markup=await update_follow_menu_keyboard())

def randomString():
    rndLetters = (random.choice(string.ascii_uppercase) for _ in range(6))
    return "".join(rndLetters)

def get_captha():
    
    captcha = randomString()
    
    c = Claptcha(captcha, "test.ttf")
    c.write(f'{captcha}.png')
    res = open(f'{captcha}.png', 'rb')

    return [captcha, res]

async def get_price():
    reduction_full_name = {
        "TRX": "tron",
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "USDT": "binancecoin",
        "SOL": "solana",
        "XRP": "ripple",
        "ADA": "cardano",
        "DOGE": "dogecoin",
        "TON": "the-open-network",
    }
    async with httpx.AsyncClient() as client:
        url_coin_gecko = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency={currency}&ids={reduction_full_name[cryptocurrency.upper()]}"
        response = await client.get(url_coin_gecko)
        price = response.json()[0]["current_price"]
        return Decimal(price)


async def main_message(user_id):
    referrals = len(await select_user_id_where_referrer_id_and_referrer_bonus_1(user_id))
    balance = await select_user_balance_where_user_id(user_id)
    balance_currency = Decimal(balance * await get_price()).quantize(Decimal("0.01")).normalize()
    if language == "RUS":
        if channel_with_feedback:
            await bot.send_message(user_id,
                                   "<b>🥳 Дарите подарки и зарабатывайте</b>\n\n"
                                   f"<b>Отправляйте друзьям подарки и получайте криптовалюту. Вывод станет доступен при накоплении <code>{float(minimal_withdrawal_amount)} {cryptocurrency}</code> на балансе.</b>\n\n"
                                   f"<b>👤Ваша реферальная ссылка:</b>\n"
                                   f"<b><code>https://t.me/{(await bot.get_me())['username']}?start={user_id}</code></b>\n\n"
                                   f"<b>🚀Отзывы о нас: {channel_with_feedback}</b>\n\n"
                                   f"<b>У вас <code>{referrals}</code> подтвержденных рефералов</b>\n\n"
                                   f"<b>Ваш баланс: <code>{float(balance)} {cryptocurrency}</code>   (<code>{float(balance_currency)}{currency_sign}</code>)</b>\n\n"
                                   f"<b>Ваш ID: <code>{user_id}</code></b>",
                                   reply_markup=await main_menu_keyboard())
        else:
            await bot.send_message(user_id,
                                   "<b>🥳 Дарите подарки и зарабатывайте</b>\n\n"
                                   f"<b>Отправляйте друзьям подарки и получайте криптовалюту. Вывод станет доступен при накоплении <code>{float(minimal_withdrawal_amount)} {cryptocurrency}</code> на балансе.</b>\n\n"
                                   f"<b>👤Ваша реферальная ссылка:</b>\n"
                                   f"<b><code>https://t.me/{(await bot.get_me())['username']}?start={user_id}</code></b>\n\n"
                                   f"<b>У вас <code>{referrals}</code> подтвержденных рефералов</b>\n\n"
                                   f"<b>Ваш баланс: <code>{float(balance)} {cryptocurrency}</code>   (<code>{float(balance_currency)}{currency_sign}</code>)</b>\n\n"
                                   f"<b>Ваш ID: <code>{user_id}</code></b>",
                                   reply_markup=await main_menu_keyboard())
    elif language == "ENG":
        if channel_with_feedback:
            await bot.send_message(user_id,
                                   "<b>🥳 Give gifts and earn</b>\n\n"
                                   f"<b>Send gifts to your friends and receive cryptocurrency. The output will become available when accumulating <code>{float(minimal_withdrawal_amount)} {cryptocurrency}</code> on balance.</b>\n\n"
                                   f"<b>👤Your referral link:</b>\n"
                                   f"<b><code>https://t.me/{(await bot.get_me())['username']}?start={user_id}</code></b>\n\n"
                                   f"<b>🚀Reviews about us: {channel_with_feedback}</b>\n\n"
                                   f"<b>You have <code>{referrals}</code> onfirmed referrals</b>\n\n"
                                   f"<b>Your balance: <code>{float(balance)} {cryptocurrency}</code>   (<code>{float(balance_currency)}{currency_sign}</code>)</b>\n\n"
                                   f"<b>Your ID: <code>{user_id}</code></b>",
                                   reply_markup=await main_menu_keyboard())
        else:
            await bot.send_message(user_id,
                                   "<b>🥳 Give gifts and earn</b>\n\n"
                                   f"<b>Send gifts to your friends and receive cryptocurrency. The output will become available when accumulating <code>{float(minimal_withdrawal_amount)} {cryptocurrency}</code> on balance.</b>\n\n"
                                   f"<b>👤Your referral link:</b>\n"
                                   f"<b><code>https://t.me/{(await bot.get_me())['username']}?start={user_id}</code></b>\n\n"
                                   f"<b>You have <code>{referrals}</code> onfirmed referrals</b>\n\n"
                                   f"<b>Your balance: <code>{float(balance)} {cryptocurrency}</code>   (<code>{float(balance_currency)}{currency_sign}</code>)</b>\n\n"
                                   f"<b>Your ID: <code>{user_id}</code></b>",
                                   reply_markup=await main_menu_keyboard())


@dp.message_handler(commands="admin", state="*")
async def admin_menu(message: types.Message, state: FSMContext):
    await state.finish()
    user_id = message.from_user.id
    for i in range(0, len(id_admins)):
        if user_id == id_admins[i]:
            id_admin = id_admins[i]
            await bot.send_message(id_admin, "<b>Включено админ меню</b>", reply_markup=await admin_menu_keyboard())


@dp.message_handler(commands="start", state="*")
async def start_command(message: types.Message, state: FSMContext):
    await state.finish()
    data = get_captha()
    captcha = data[0]
    await state.update_data(captcha=captcha)
    await state.update_data(mess=message.text)

    ph = data[1]

    await message.answer_photo(photo=ph,caption="Введите текст с картинки")
    os.remove(f"{captcha}.png")
    await state.set_state("check")
    
    

@dp.message_handler(state="check")
async def get_username(message: types.Message, state: FSMContext):
    data = await state.get_data()
    print(data['mess'])
    if message.text.lower() == data['captcha'].lower():
        user_id = message.from_user.id
        user_username = message.from_user.username
        entry_date = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        if user_username is not None:
            user_username = user_username.lower()
        if await select_user_id_where_user_id(user_id) is None:
            try:
                referrer = int(data['mess'].split()[1])
                if user_id != referrer:
                    referrer_bonus = 0
                else:
                    referrer = None
                    referrer_bonus = 1
            except:
                referrer = None
                referrer_bonus = 1
            await adding_data(user_id, user_username, referrer, referrer_bonus, entry_date)
        if await check_follow_channels(user_id):
            await main_message(user_id)
        else:
            await no_follow_message(user_id)
    else:
        await message.answer(f"Не верно\nВаш ответ:{message.text.lower()}\nПравильный ответ:{data['captcha'].lower()}\n\nНапишите /start и повторите попытку")
    await state.finish()

### ---___--- ЮЗЕР МЕНЮ ---___--- ###


@dp.callback_query_handler(text="update_balance")
async def update_balance_call(call: types.CallbackQuery):
    user_id = call.from_user.id
    user_username = call.from_user.username
    if user_username is not None:
        user_username = user_username.lower()
    await changing_username_where_user_id(user_username, user_id)
    if await check_follow_channels(user_id):
        await main_message(user_id)
    else:
        await no_follow_message(user_id)


@dp.callback_query_handler(text="withdraw_funds")
async def withdraw_funds_call(call: types.CallbackQuery):
    user_id = call.from_user.id
    if await select_user_balance_where_user_id(user_id) >= minimal_withdrawal_amount:
        if language == "RUS":
            await bot.send_message(user_id, "Введите сумму вывода баланса", reply_markup=await deleted_message_menu_keyboard())
        elif language == "ENG":
            await bot.send_message(user_id, "Enter the balance withdrawal amount", reply_markup=await deleted_message_menu_keyboard())
        await withdrawal_of_balance.withdrawal_amount_state.set()
    else:
        if language == "RUS":
            await bot.answer_callback_query(call.id, text="Недостаточно средств")
        elif language == "ENG":
            await bot.answer_callback_query(call.id, text="Insufficient funds")


@dp.callback_query_handler(text="update_follow")
async def update_follow_call(call: types.CallbackQuery):
    user_id = call.from_user.id
    user_username = call.from_user.username
    await call.message.delete()
    if await check_follow_channels(user_id):
        if await select_referrer_bonus_where_user_id(user_id) == 0:
            await adding_user_balance_where_user_id(await select_referrer_id_where_user_id(user_id))
            await changing_referrer_bonus_where_user_id(1, user_id)
            await adding_user_balance_where_user_id(user_id)
            balance = await select_user_balance_where_user_id(await select_referrer_id_where_user_id(user_id))
            balance_currency = Decimal(balance * await get_price()).quantize(Decimal("0.01")).normalize()
            await main_message(user_id)
            if user_username is not None:
                if language == "RUS":
                    await bot.send_message(await select_referrer_id_where_user_id(user_id),
                                           f"<b>У вас новый Реферал ({user_username.lower()}), ваш баланс пополнен на <code>{amount_per_one} {cryptocurrency}</code></b>\n"
                                           f"<b>Ваш баланс: <code>{float(balance)} {cryptocurrency}</code>   (<code>{float(balance_currency)}{currency_sign}</code>)</b>",
                                           reply_markup=await deleted_message_menu_keyboard())
                elif language == "ENG":
                    await bot.send_message(await select_referrer_id_where_user_id(user_id),
                                           f"<b>You have a new Referral ({user_username.lower()}), your balance is topped up on <code>{amount_per_one} {cryptocurrency}</code></b>\n"
                                           f"<b>Your balance: <code>{float(balance)} {cryptocurrency}</code>   (<code>{float(balance_currency)}{currency_sign}</code>)</b>",
                                           reply_markup=await deleted_message_menu_keyboard())
            else:
                if language == "RUS":
                    await bot.send_message(await select_referrer_id_where_user_id(user_id),
                                           f"<b>У вас новый Реферал ({user_id}), ваш баланс пополнен на <code>{amount_per_one} {cryptocurrency}</code></b>\n"
                                           f"<b>Ваш баланс: <code>{float(balance)} {cryptocurrency}</code>   (<code>{float(balance_currency)}{currency_sign}</code>)</b>",
                                           reply_markup=await deleted_message_menu_keyboard())
                elif language == "ENG":
                    await bot.send_message(await select_referrer_id_where_user_id(user_id),
                                           f"<b>You have a new Referral ({user_id}), your balance is topped up on <code>{amount_per_one} {cryptocurrency}</code></b>\n"
                                           f"<b>Your balance: <code>{float(balance)} {cryptocurrency}</code>   (<code>{float(balance_currency)}{currency_sign}</code>)</b>",
                                           reply_markup=await deleted_message_menu_keyboard())
        else:
            await main_message(user_id)
    else:
        await no_follow_message(user_id)


@dp.message_handler(state=withdrawal_of_balance.withdrawal_amount_state)
async def withdraw_funds_call(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_username = message.from_user.username
    withdrawal_amount = message.text
    balance = await select_user_balance_where_user_id(user_id)
    if withdrawal_amount.replace(',', '').replace('.', '').isnumeric():
        withdrawal_amount = Decimal(withdrawal_amount).quantize(Decimal("0.0000001")).normalize()
        if balance >= withdrawal_amount >= minimal_withdrawal_amount:
            await changing_user_balance_where_user_id((float(balance) - float(withdrawal_amount)), user_id)
            await message.delete()
            if language == "RUS":
                await bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id - 1, text=
                "<b>Заявка на вывод средств:</b>\n"
                f"<b>Сумма: <code>{float(withdrawal_amount)} {cryptocurrency}</code></b>\n"
                f"<b>Ваш ID: {user_id}</b>\n"
                f"<b>В случае каких либо проблем с выводом необходимо обратиться: {technical_support}</b>\n",
                                            reply_markup=await deleted_message_menu_keyboard())
            elif language == "ENG":
                await bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id - 1, text=
                "<b>Request for withdrawal of funds:</b>\n"
                f"<b>The amount: <code>{float(withdrawal_amount)} {cryptocurrency}</code></b>\n"
                f"<b>Your ID: {user_id}</b>\n"
                f"<b>In case of any problems with the withdrawal, you need to contact: {technical_support}</b>\n",
                                            reply_markup=await deleted_message_menu_keyboard())

            for i in range(len(id_admins)):
                admin_id = id_admins[i]
                if user_username is not None:
                    await bot.send_message(admin_id,
                                           f"<b>Пользователь @{user_username} ({user_id}) хочет вывести <code>{float(withdrawal_amount)} {cryptocurrency}</code></b>",
                                           reply_markup=await deleted_message_menu_keyboard())
                else:
                    await bot.send_message(admin_id,
                                           f"<b>Пользователь {user_id} хочет вывести <code>{float(withdrawal_amount)} {cryptocurrency}</code></b>",
                                           reply_markup=await deleted_message_menu_keyboard())
            await state.finish()
        else:
            if withdrawal_amount > balance:
                await message.delete()
                if language == "RUS":
                    await bot.send_message(user_id, "Недостаточно средств", reply_markup=await deleted_message_menu_keyboard())
                elif language == "ENG":
                    await bot.send_message(user_id, "Insufficient funds", reply_markup=await deleted_message_menu_keyboard())
            elif minimal_withdrawal_amount > withdrawal_amount:
                await message.delete()
                if language == "RUS":
                    await bot.send_message(user_id, f"Минимальная сумма вывода средств: <code>{float(minimal_withdrawal_amount)} {cryptocurrency}</code>", reply_markup=await deleted_message_menu_keyboard())
                elif language == "ENG":
                    await bot.send_message(user_id, f"Minimum withdrawal amount: <code>{float(minimal_withdrawal_amount)} {cryptocurrency}</code>", reply_markup=await deleted_message_menu_keyboard())

    else:
        if language == "RUS":
            await bot.send_message(user_id, f"Минимальная сумма вывода средств: <code>{float(minimal_withdrawal_amount)} {cryptocurrency}</code>", reply_markup=await deleted_message_menu_keyboard())
        elif language == "ENG":
            await bot.send_message(user_id, f"Minimum withdrawal amount: <code>{float(minimal_withdrawal_amount)} {cryptocurrency}</code>", reply_markup=await deleted_message_menu_keyboard())


### ---___--- АДМИН МЕНЮ ---___--- ###


@dp.callback_query_handler(text="number_users")
async def number_users_admin(call: types.CallbackQuery):
    admin_id = call.from_user.id
    await bot.send_message(admin_id, f"<b>Всего пользователей</b>: {len(await select_all_user_id())}", reply_markup=await info_menu_keyboard())


@dp.callback_query_handler(text="update_info")
async def update_number_users_admin(call: types.CallbackQuery):
    admin_id = call.from_user.id
    await call.message.delete()
    await bot.send_message(admin_id, f"<b>Всего пользователей: {len(await select_all_user_id())}</b>", reply_markup=await info_menu_keyboard())


@dp.callback_query_handler(text="download_database")
async def download_database_admin(call: types.CallbackQuery):
    admin_id = call.from_user.id
    await bot.send_document(admin_id, open("database.db", "rb"), reply_markup=await deleted_message_menu_keyboard())


@dp.callback_query_handler(text="private_message")
async def private_message_admin(call: types.CallbackQuery):
    admin_id = call.from_user.id
    await bot.send_message(admin_id, "<b>Введите ID пользователя, либо Username</b>", reply_markup=await deleted_message_menu_keyboard())
    await private_message.id_or_username_state.set()


@dp.callback_query_handler(text="mailing")
async def send_all_admin(call: types.CallbackQuery):
    admin_id = call.from_user.id
    await bot.send_message(admin_id, "<b>Введите сообещние для рассылки</b>", reply_markup=await deleted_message_menu_keyboard())
    await receiving_a_message.receiving_message_state.set()


@dp.callback_query_handler(text="changing_balance")
async def changing_balance_admin(call: types.CallbackQuery):
    admin_id = call.from_user.id
    await bot.send_message(admin_id, "<b>Введите ID пользователя, либо Username</b>", reply_markup=await deleted_message_menu_keyboard())
    await changing_the_balance.id_or_username_state.set()


@dp.message_handler(state=private_message.id_or_username_state)
async def private_message_id_or_username_admin_handler(message: types.Message, state: FSMContext):
    username_or_id = message.text.lower()
    await message.delete()
    if await select_user_id_where_user_id(username_or_id) is not None or await select_user_username_where_user_name(
            username_or_id) is not None:
        await bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id - 1,
                                    text="<b>Введите сообщение для отправки</b>",
                                    reply_markup=await deleted_message_menu_keyboard())
        await state.update_data(username_or_id=username_or_id)
        await private_message.private_message_state.set()
    else:
        await bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id - 1,
                                    text="<b>Пользователь не найден</b>",
                                    reply_markup=await deleted_message_menu_keyboard())
        await state.finish()


@dp.message_handler(state=private_message.private_message_state)
async def private_message_private_message_admin_handler(message: types.Message, state: FSMContext):
    private_message_text = message.text
    data = await state.get_data()
    username_or_id = data.get("username_or_id")
    await message.delete()
    if not username_or_id.isnumeric():
        username_or_id = await select_user_id_where_user_username(username_or_id)
    await bot.send_message(username_or_id, private_message_text, reply_markup=await deleted_message_menu_keyboard())
    await bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id - 2,
                                text=f"<b>Пользователю {username_or_id} отправили сообщение {private_message_text}</b>",
                                reply_markup=await deleted_message_menu_keyboard())
    await state.finish()


@dp.message_handler(state=receiving_a_message.receiving_message_state)
async def receiving_a_message_receiving_message_admin_handler(message: types.Message, state: FSMContext):
    admin_id = message.from_user.id
    text = message.text
    await state.finish()
    await message.delete()
    for users in await select_all_user_id():
        try:
            await bot.send_message(chat_id=users[0], text=text, reply_markup=await deleted_message_menu_keyboard())
        except:
            pass
    await bot.send_message(admin_id, "<b>Массовая рассылка успешно завершена!</b>", reply_markup=await deleted_message_menu_keyboard())


@dp.message_handler(state=changing_the_balance.id_or_username_state)
async def changing_the_balance_id_or_username_admin_handler(message: types.Message, state: FSMContext):
    username_or_id = message.text.lower()
    await message.delete()
    if await select_user_id_where_user_id(username_or_id) is not None or await select_user_username_where_user_name(username_or_id) is not None:
        await bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id - 1,
                                    text="<b>Введите число на какое изменить баланс</b>",
                                    reply_markup=await deleted_message_menu_keyboard())
        await state.update_data(username_or_id=username_or_id)
        await changing_the_balance.change_amount_state.set()
    else:
        await bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id - 1,
                                    text="<b>Пользователь не найден</b>",
                                    reply_markup=await deleted_message_menu_keyboard())
        await state.finish()


@dp.message_handler(state=changing_the_balance.change_amount_state)
async def changing_the_balance_change_amount_admin_handler(message: types.Message, state: FSMContext):
    change_amount = message.text
    data = await state.get_data()
    username_or_id = data.get("username_or_id")
    await message.delete()
    if not username_or_id.isnumeric():
        username_or_id = await select_user_id_where_user_username(username_or_id)
    if change_amount.replace(',', '').replace('.', '').isnumeric():
        await changing_user_balance_where_user_id(float(change_amount), username_or_id)
        await bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id - 2,
                                    text=f"<b>У пользователя {username_or_id} баланс {change_amount}</b>",
                                    reply_markup=await deleted_message_menu_keyboard())
    else:
        await bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id - 2,
                                    text=f"<b>{change_amount} - не число</b>",
                                    reply_markup=await deleted_message_menu_keyboard())
    await state.finish()


### ---___--- УДАЛЕНИЕ СООБЩЕНИЙ ---___--- ###


@dp.callback_query_handler(text="deleted_message", state="*")
async def deleted_message_call(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()


### ---___--- ИНЛАЙН СООБЩЕНИЕ ---___--- ###


@dp.inline_handler()
async def inline_handler(query: types.InlineQuery):
    if language == "RUS":
        all_text = ["🥳 Хочу подарить тебе немного криптовалюты",
                    f"🥳 Привет, хочу подарить тебе немного криптовалюты {cryptocurrency}",
                    f"🥳 Привет, мне тоже захотелось присоединиться к этому тренду и подарить тебе немного криптовалюты {cryptocurrency}",
                    f"🥳 Привет, у меня для тебя есть подарок — немного криптовалюты {cryptocurrency}"]

    elif language == "ENG":
        all_text = ["🥳 I want to give you some cryptocurrency",
                    f"🥳 Hi, I want to give you some cryptocurrency {cryptocurrency}",
                    f"🥳 Hi, I also wanted to join this trend and give you some cryptocurrency {cryptocurrency}",
                    f"🥳 Hi, I have a gift for you — a little cryptocurrency {cryptocurrency}"]

    random_text = random.choice(all_text)
    text = query.query or "echo"
    result_id: str = hashlib.md5(text.encode()).hexdigest()

    articles = [types.InlineQueryResultArticle(
        id=result_id,
        title=random_text,
        reply_markup=await get_gift_menu_keyboard((await bot.get_me())["username"], query.from_user.id),
        input_message_content=types.InputMessageContent(
            message_text=random_text))]
    await query.answer(articles, cache_time=1, is_personal=True)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(create_database())
    executor.start_polling(dp)
