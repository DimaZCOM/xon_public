import telebot
from telebot import types
import os
from pymongo import MongoClient
import utils
from utils import heroku_check, log
import random

# configuring variables
TOKEN = utils.TOKEN
admin_id = utils.admin_id
uri = utils.uri
bot_id = utils.bot_id
ban_id = utils.ban_id
#
#
# Set client & db up
myclient = MongoClient(uri)
mydb = myclient["userdb"]
mycol = mydb["users"]
bot = telebot.TeleBot(TOKEN)


banned = ["508501966"]


@bot.message_handler(commands=["start"])
def start(message):
    if str(message.from_user.id) not in banned:
        log(message)
        txt = """
        * Версия 2.0 *. Если вдруг есть идеи того, что вы хотите увидеть в боте, можете просто написать в личку боту или [мне](https://t.me/xon_usr)
        * Функционал *: Сапер (/minesweeper)

        Исходный код: [тутачки](https://github.com/xon-dev/xon_public)
        """
        if str(message.chat.id) != admin_id:
            bot.reply_to(message, txt, parse_mode="markdown")


@bot.message_handler(commands=["minesweeper"])
def size_menu(message):
    if str(message.from_user.id) not in banned:
        if str(message.chat.id) != admin_id:
            log(message)
        find = mycol.find_one({"chat": message.chat.id})
        if str(find) == "None":
            # Buttons w sizes. Return 's' + choice
            choice = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton(text="4", callback_data="s4")
            button2 = types.InlineKeyboardButton(text="5", callback_data="s5")
            choice.row(button1, button2)
            button3 = types.InlineKeyboardButton(text="6", callback_data="s6")
            button4 = types.InlineKeyboardButton(text="7", callback_data="s7")
            choice.row(button3, button4)
            button5 = types.InlineKeyboardButton(text="8", callback_data="s8")
            choice.row(button5)
            if str(message.from_user.id) != bot_id:
                bot.send_message(
                    message.chat.id, "Choose size:", reply_markup=choice
                )
            else:
                bot.edit_message_text(
                    "Choose size:",
                    message.chat.id,
                    message.message_id,
                    reply_markup=choice,
                )
        else:
            choice = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton(
                text="Доиграть прошлую игру", callback_data="prevgame"
            )
            button2 = types.InlineKeyboardButton(
                text="Начать новую игру", callback_data="newgame"
            )
            choice.row(button1, button2)
            bot.send_message(
                message.chat.id,
                "Была найдена ваша предыдущая игра в этом чате. Вы можете начать новую или продолжить незавершенную",
                reply_markup=choice,
            )


@bot.message_handler(content_types=["text"])
def frwrd(message):
    if str(message.from_user.id) not in banned:
        bot.forward_message(admin_id, message.chat.id, message.message_id)


@bot.callback_query_handler(lambda query: query.data == "newgame")
def new_game(call):
    if str(call.message.from_user.id) not in banned:
        mycol.delete_one({"chat": call.message.chat.id})
        size_menu(call.message)


@bot.callback_query_handler(lambda query: query.data == "prevgame")
def prev_game(call):
    if str(message.from_user.id) not in banned:
        find = mycol.find_one({"chat": call.message.chat.id})
        find["message"] = call.message.message_id
        mycol.update_one(
            {"chat": call.message.chat.id},
            {"$set": {"message": call.message.message_id}},
        )
        field = find["field"]
        size = find["size"]
        keyboard = utils.board(size, field)
        cid = call.message.chat.id
        mid = call.message.message_id
        bot.edit_message_text(
            chat_id=cid, message_id=mid, text="Field:", reply_markup=keyboard,
        )


@bot.callback_query_handler(lambda query: "s" in query.data)
def fieldbegin(call):
    if str(call.message.from_user.id) not in banned:
        # Takes size from callback
        size = int(call.data[1])
        field = utils.empty_field(size)
        minbomb = int(size * size / 6)
        maxbomb = int(size * size / 4)
        # random mines from +-normal range
        mines = random.randint(minbomb, maxbomb)
        # generating field w mines
        minefield = random.sample(field, mines)
        for i in range(len(field)):
            for j in range(len(minefield)):
                if field[i] == minefield[j]:
                    field[i]["is_mine"] = 1
        c = 0
        for i in range(size):
            for j in range(size):
                field[c]["count_mines"] = utils.minec(field, size, i, j)
                c += 1
        keyboard = utils.board(size, field)
        cid = call.message.chat.id
        mid = call.message.message_id
        bot.edit_message_text(
            chat_id=cid, message_id=mid, text="Field:", reply_markup=keyboard,
        )
        find = mycol.find_one({"chat": call.message.chat.id})
        if str(find) == "None":
            user = {"message": mid, "chat": cid, "size": size, "field": field}
            mycol.insert_one(user)


@bot.callback_query_handler(lambda query: "z" in query.data)
def fieldgame(call):
    if str(call.message.from_user.id) not in banned:
        find = mycol.find_one({"chat": call.message.chat.id})
        if call.message.message_id != find["message"]:
            bot.edit_message_text(
                "Use last message from chat or run /minesweeper to play",
                call.message.chat.id,
                call.message.message_id,
            )
        else:
            size = int(call.data[1])
            x = int(call.data[2])
            y = int(call.data[3])
            if str(find) != "None":
                field = find["field"]
                field[x * size + y]["is_opened"] = 1
                if (
                    field[x * size + y]["is_mine"] == 1
                    and field[x * size + y]["is_opened"] == 1
                ):
                    mycol.delete_one({"chat": call.message.chat.id})
                    keyboard = utils.endboard(size, field)
                    bot.answer_callback_query(
                        callback_query_id=call.id, text="You lost", show_alert=1
                    )
                    button = types.InlineKeyboardButton(
                        text="Начать новую игру", callback_data="newgame"
                    )
                    keyboard.row(button)
                    cid = call.message.chat.id
                    mid = call.message.message_id
                    bot.edit_message_text(
                        chat_id=cid,
                        message_id=mid,
                        text="Field:",
                        reply_markup=keyboard,
                    )
                else:
                    nopened = 0
                    minecounter = 0
                    for i in range(len(field)):
                        if field[i]["is_opened"] == 0:
                            nopened += 1
                        if field[i]["is_mine"] == 1:
                            minecounter += 1
                    if nopened == minecounter:
                        utils.winreply(call, size, field)
                        mycol.delete_one({"chat": call.message.chat.id})
                    else:
                        utils.opengame(field, size, x, y)
                        nopened = 0
                        minecounter = 0
                        for i in range(len(field)):
                            if field[i]["is_opened"] == 0:
                                nopened += 1
                            if field[i]["is_mine"] == 1:
                                minecounter += 1
                        if nopened == minecounter:
                            utils.winreply(call, size, field)
                            mycol.delete_one({"chat": call.message.chat.id})
                        else:
                            keyboard = utils.board(size, field)
                            cid = call.message.chat.id
                            mid = call.message.message_id
                            bot.edit_message_text(
                                chat_id=cid,
                                message_id=mid,
                                text="Field:",
                                reply_markup=keyboard,
                            )
                            find = mycol.find_one(
                                {"chat": call.message.chat.id}
                            )
                            mycol.update_one(
                                {"chat": call.message.chat.id},
                                {"$set": {"field": field}},
                            )
            else:
                bot.edit_message_text(
                    "ERROR", call.message.chat.id, call.message.message_id
                )


@bot.callback_query_handler(lambda query: query.data == "OK")
def okay(call):
    bot.answer_callback_query(call.id, "Done")


# run webhook server/polling
if heroku_check():
    from flask import Flask, request

    server = Flask(__name__)

    @server.route("/" + TOKEN, methods=["POST"])
    def getMessage():
        bot.process_new_updates(
            [
                telebot.types.Update.de_json(
                    request.stream.read().decode("utf-8")
                )
            ]
        )
        return "<h1>ЖИВ</h1>", 200

    @server.route("/")
    def webhook():
        bot.remove_webhook()
        bot.set_webhook(url=str(utils.url) + TOKEN)
        return "<h2>жив</h2>", 200

    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
else:
    bot.remove_webhook()
    bot.polling(none_stop=True)
