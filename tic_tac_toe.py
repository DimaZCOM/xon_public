import os
import telebot
from telebot import types
from utils import heroku_check
import random
import utils
from pymongo import MongoClient


if heroku_check():
    TOKEN = os.environ["TOKEN"]
    url = os.environ["URL"]
    admin_id = os.environ["ID"]
    uri = os.environ["MONGODB_URI"]
    bot_id = os.environ["BOT_ID"]
else:
    import config

    uri = config.mongouri
    TOKEN = config.token
    admin_id = config.admin_id
    bot_id = config.bot_id

bot = telebot.TeleBot(TOKEN)
pairs = utils.pairs


def genstart():
    field = []
    for i in range(3):
        for j in range(3):
            field.append({"n": i, "m": j, "value": 0})
    return field


def genboard(field, usermove, first, second):
    c = 0
    keyboard = types.InlineKeyboardMarkup()
    for i in range(3):
        rows = []
        for j in range(3):
            if field[c]["value"] == 0:
                text = "⏺"
                if usermove == first:
                    data = str(i) + "*" + str(j)
                else:
                    data = str(i) + "/" + str(j)
            elif field[c]["value"] == 1:
                text = "❌"
                data = "OK"
            elif field[c]["value"] == 2:
                text = "⭕️"
                data = "OK"
            rows.append(
                types.InlineKeyboardButton(text=text, callback_data=data)
            )
            c += 1
        keyboard.row(*rows)
    return keyboard


def board(field, usermove, first, second):
    c = 0
    keyboard = types.InlineKeyboardMarkup()
    for i in range(3):
        rows = []
        for j in range(3):
            if field[c]["value"] == 0:
                text = "⏺"
            elif field[c]["value"] == 1:
                text = "❌"
            elif field[c]["value"] == 2:
                text = "⭕️"
            rows.append(
                types.InlineKeyboardButton(text=text, callback_data="OK")
            )
            c += 1
        keyboard.row(*rows)
    return keyboard


def begintic(usr2, usr1):
    rand = random.randint(0, 1)
    if rand == 0:
        first = usr1
        second = usr2
    else:
        first = usr2
        second = usr1
    usermove = first
    field = genstart()
    pairs.update_one({"id": message.from_user.id})
    keyboard1 = genboard(field, usermove, first, second)
    keyboard2 = board(field, usermove, first, second)

    button = types.InlineKeyboardButton(
        text="Получить ход противника",
        callback_data="getmove" + str(usr2) + str(usr1),
    )
    keyboard2.row(button)
    bot.send_message(first, "Твой ход:", reply_markup=keyboard1)
    bot.send_message(second, "Ход противника:", reply_markup=keyboard2)
