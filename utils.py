import os
import telebot
import pytz
from datetime import datetime
from pymongo import MongoClient


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
else:
    import config

    uri = config.mongouri
    TOKEN = config.token
    admin_id = config.admin_id
    bot_id = config.bot_id

bot = telebot.TeleBot(TOKEN)

myclient = MongoClient(uri)
mydb = myclient["userdb"]
mycol = mydb["users"]
bancol = mydb["ban"]
pairs = mydb["pairs"]


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
