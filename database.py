from decimal import *

import aiosqlite

from config import *


### ---___--- СОЗДАНИЕ БАЗЫ ДАННЫХ ---___--- ###
async def create_database():
    async with aiosqlite.connect("database.db") as db:
        await db.execute("""CREATE TABLE IF NOT EXISTS database(
                            basic_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                            user_id BIGINT NOT NULL,
                            user_balance DECIMAL DEFAULT 0,
                            user_username TEXT,
                            referrer_id INTEGER,
                            referrer_bonus INTEGER DEFAULT 0,
                            entry_date DATE)""")
        await db.commit()


### ---___--- ДОБАВЛЕНИЕ ДАННЫХ В БАЗУ ДАННЫХ ---___--- ###
async def adding_data(user_id, user_username, referrer, referrer_bonus, entry_date):
    async with aiosqlite.connect("database.db") as db:
        await db.execute(
            "INSERT INTO database (user_id, user_username, user_balance, referrer_id, referrer_bonus, entry_date) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, user_username, 0, referrer, referrer_bonus, entry_date))
        await db.commit()


### ---___--- ВЫБОР ЧЕГО-ТО ИЗ БАЗЫ ДАННЫХ ---___--- ###
async def select_all_user_id():
    async with aiosqlite.connect("database.db") as db:
        async with db.execute("SELECT user_id FROM database") as cursor:
            all_users = await cursor.fetchall()
            return all_users


async def select_user_id_where_user_id(user_id):
    async with aiosqlite.connect("database.db") as db:
        async with db.execute("SELECT user_id FROM database WHERE user_id = ?", (user_id,)) as cursor:
            user_id = await cursor.fetchone()
            return user_id


async def select_user_username_where_user_name(user_username):
    async with aiosqlite.connect("database.db") as db:
        async with db.execute("SELECT user_username FROM database WHERE user_username = ?", (user_username,)) as cursor:
            user_username = await cursor.fetchone()
            return user_username


async def select_user_id_where_user_username(user_username):
    async with aiosqlite.connect("database.db") as db:
        async with db.execute("SELECT user_id FROM database WHERE user_username = ?", (user_username,)) as cursor:
            user_id = await cursor.fetchone()
            return user_id[0]


async def select_user_balance_where_user_id(user_id):
    async with aiosqlite.connect("database.db") as db:
        async with db.execute("SELECT user_balance FROM database WHERE user_id = ?", (user_id,)) as cursor:
            user_balance = await cursor.fetchone()
            user_balance = Decimal(user_balance[0]).quantize(Decimal("0.0000001")).normalize()
            return user_balance


async def select_referrer_id_where_user_id(user_id):
    async with aiosqlite.connect("database.db") as db:
        async with db.execute("SELECT referrer_id FROM database WHERE user_id = ?", (user_id,)) as cursor:
            referral = await cursor.fetchone()
            return referral[0]


async def select_referrer_bonus_where_user_id(user_id):
    async with aiosqlite.connect("database.db") as db:
        async with db.execute("SELECT referrer_bonus FROM database WHERE user_id = ?", (user_id,)) as cursor:
            referrer_bonus = await cursor.fetchone()
            return referrer_bonus[0]


async def select_user_id_where_referrer_id_and_referrer_bonus_1(user_id):
    async with aiosqlite.connect("database.db") as db:
        async with db.execute("SELECT user_id FROM database WHERE referrer_id = ? AND referrer_bonus = 1",
                              (user_id,)) as cursor:
            number_referrals = await cursor.fetchall()
            return number_referrals


### ---___--- ИЗМЕНЕНИЕ ЧЕГО-ТО ИЗ БАЗЫ ДАННЫХ ---___--- ###
async def changing_username_where_user_id(user_username, user_id):
    async with aiosqlite.connect("database.db") as db:
        await db.execute("UPDATE database SET user_username = ? WHERE user_id = ?", (user_username, user_id))
        await db.commit()


async def changing_referrer_bonus_where_user_id(referrer_bonus, user_id):
    async with aiosqlite.connect("database.db") as db:
        await db.execute("UPDATE database SET referrer_bonus = ? WHERE user_id = ?", (referrer_bonus, user_id))
        await db.commit()


async def changing_user_balance_where_user_id(change_amount, username_or_id):
    async with aiosqlite.connect("database.db") as db:
        await db.execute("UPDATE database SET user_balance = ? WHERE user_id = ?", (change_amount, username_or_id))
        await db.commit()


async def adding_user_balance_where_user_id(referral):
    async with aiosqlite.connect("database.db") as db:
        await db.execute("UPDATE database SET user_balance = user_balance + ? WHERE user_id = ?",
                         (amount_per_one, referral,))
        await db.commit()
