import os
import telebot
from telebot import types
import pytz
from datetime import datetime


def heroku_check():
    r"""
    true if app has deployed on heroku
    """
    return "HEROKU" in list(os.environ.keys())


if heroku_check():
    TOKEN = os.environ["TOKEN"]
    url = os.environ["URL"]
    admin_id = os.environ["ID"]
    uri = os.environ["MONGODB_URI"]
    bot_id = os.environ["BOT_ID"]
    ban_id = os.environ["BAN"]
else:
    import config

    ban_id = config.ban_id
    uri = config.mongouri
    TOKEN = config.token
    admin_id = config.admin_id
    bot_id = config.bot_id

bot = telebot.TeleBot(TOKEN)


def html_message(
    datetime, ctype, cid, cusername, name, lname, username, id, text
):
    return f"""
    <b>NEW MESSAGE</b>
    <b>TIME</b>: <code>{datetime}</code>
    <b>CHAT</b>
    - TYPE: <code>{ctype}</code>
    - ID: <code>{str(cid)}</code>
    - NAME: @{str(cusername)}
    <b>USER</b>
    - First: |<code>{name}</code>|
    - Last:  |<code>{lname}</code>|
    - Username: @{str(username)}
    - ID: <code>{str(id)}</code>
    MESSAGE TEXT: |<code>{text}</code>|"""


def log(message):
    if str(message.chat.id) != ban_id:
        kyiv = pytz.timezone("Europe/Kiev")
        kyiv_time = kyiv.localize(datetime.now())
        date = kyiv_time.strftime("%d %B %Y %H:%M:%S")
        html = html_message(
            date,
            message.chat.type,
            message.chat.id,
            message.chat.username,
            message.from_user.first_name,
            message.from_user.last_name,
            message.from_user.username,
            message.from_user.id,
            message.text,
        )
        bot.send_message(admin_id, html, parse_mode="html")


def minec(field, size, n, m):
    c = size * n + m
    cmine = 0
    if n != 0 and m != 0:
        if field[c - size - 1]["is_mine"] == 1:
            cmine += 1
    if n != 0:
        if field[c - size]["is_mine"] == 1:
            cmine += 1
    if n != 0 and m != size - 1:
        if field[c - size + 1]["is_mine"] == 1:
            cmine += 1
    if m != size - 1:
        if field[c + 1]["is_mine"] == 1:
            cmine += 1
    if n != size - 1 and m != size - 1:
        if field[c + size + 1]["is_mine"] == 1:
            cmine += 1
    if n != size - 1:
        if field[c + size]["is_mine"] == 1:
            cmine += 1
    if n != size - 1 and m != 0:
        if field[c + size - 1]["is_mine"] == 1:
            cmine += 1
    if m != 0:
        if field[c - 1]["is_mine"] == 1:
            cmine += 1
    print("cmine=", cmine)
    return cmine


def empty_field(size):
    field = []
    for i in range(size):
        for j in range(size):
            field.append(
                {
                    "n": i,
                    "m": j,
                    "is_opened": 0,
                    "is_mine": 0,
                    "is_found": 0,
                    "count_mines": 0,
                }
            )
    return field


def endboard(size, field):
    keyboard = types.InlineKeyboardMarkup(size)
    for i in range(size):
        rows = []
        for j in range(size):
            if field[i * size + j]["is_mine"] == 1:
                text = "💣"
            else:
                if field[i * size + j]["count_mines"] == 0:
                    text = "0️⃣"
                elif field[i * size + j]["count_mines"] == 1:
                    text = "1️⃣"
                elif field[i * size + j]["count_mines"] == 2:
                    text = "2⃣"
                elif field[i * size + j]["count_mines"] == 3:
                    text = "3⃣"
                elif field[i * size + j]["count_mines"] == 4:
                    text = "4⃣"
                elif field[i * size + j]["count_mines"] == 5:
                    text = "5⃣"
                elif field[i * size + j]["count_mines"] == 6:
                    text = "6⃣"
                elif field[i * size + j]["count_mines"] == 7:
                    text = "7⃣"
                elif field[i * size + j]["count_mines"] == 8:
                    text = "8⃣"
            rows.append(
                types.InlineKeyboardButton(text=text, callback_data="OK")
            )
        keyboard.row(*rows)
    return keyboard


def opengame(field, size, n, m):
    c = n * size + m
    field[c]["is_found"] = 1
    if field[c]["count_mines"] == 0:
        if n != 0 and m != 0:
            field[c - size - 1]["is_opened"] = 1
            if field[c - size - 1]["is_found"] != 1:
                opengame(field, size, n - 1, m - 1)
        if n != 0:
            field[c - size]["is_opened"] = 1
            if field[c - size]["is_found"] != 1:
                opengame(field, size, n - 1, m)
        if n != 0 and m != size - 1:
            field[c - size + 1]["is_opened"] = 1
            if field[c - size + 1]["is_found"] != 1:
                opengame(field, size, n - 1, m + 1)
        if m != size - 1:
            field[c + 1]["is_opened"] = 1
            if field[c + 1]["is_found"] != 1:
                opengame(field, size, n, m + 1)
        if n != size - 1 and m != size - 1:
            field[c + size + 1]["is_opened"] = 1
            if field[c + size + 1]["is_found"] != 1:
                opengame(field, size, n + 1, m + 1)
        if n != size - 1:
            field[c + size]["is_opened"] = 1
            if field[c + size]["is_found"] != 1:
                opengame(field, size, n + 1, m)
        if n != size - 1 and m != 0:
            field[c + size - 1]["is_opened"] = 1
            if field[c + size - 1]["is_found"] != 1:
                opengame(field, size, n + 1, m - 1)
        if m != 0:
            field[c - 1]["is_opened"] = 1
            if field[c - 1]["is_found"] != 1:
                opengame(field, size, n, m - 1)


def board(size, field):
    keyboard = types.InlineKeyboardMarkup(size)
    c = 0
    for i in range(size):
        rows = []
        for j in range(size):
            if field[c]["is_opened"] == 0:
                text = "⚫️"
                data = str("z" + str(size) + str(i) + str(j))
            elif field[c]["is_mine"] == 1:
                text = "💣"
                data = "OK"
            else:
                if field[i * size + j]["count_mines"] == 0:
                    text = "0️⃣"
                elif field[i * size + j]["count_mines"] == 1:
                    text = "1️⃣"
                elif field[i * size + j]["count_mines"] == 2:
                    text = "2️⃣"
                elif field[i * size + j]["count_mines"] == 3:
                    text = "3️⃣"
                elif field[i * size + j]["count_mines"] == 4:
                    text = "4️⃣"
                elif field[i * size + j]["count_mines"] == 5:
                    text = "5️⃣"
                elif field[i * size + j]["count_mines"] == 6:
                    text = "6️⃣"
                elif field[i * size + j]["count_mines"] == 7:
                    text = "7️⃣"
                elif field[i * size + j]["count_mines"] == 8:
                    text = "8️⃣"
                data = "OK"
            rows.append(
                types.InlineKeyboardButton(text=text, callback_data=data)
            )

            c += 1
        keyboard.row(*rows)
    return keyboard


def winreply(call, size, field):
    keyboard = endboard(size, field)
    bot.answer_callback_query(
        callback_query_id=call.id, text="You win!", show_alert=1,
    )
    button = types.InlineKeyboardButton(
        text="Начать новую игру", callback_data="newgame"
    )
    keyboard.row(button)
    cid = call.message.chat.id
    mid = call.message.message_id
    bot.edit_message_text(
        chat_id=cid, message_id=mid, text="Field:", reply_markup=keyboard,
    )
