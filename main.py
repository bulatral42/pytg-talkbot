import json
import os

import requests
import telebot
from telebot import types

bot_token = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(bot_token)


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.from_user.id, "👋 Привет! Я твой бот-помошник Балабобик!")  # , reply_markup=markup)


@bot.message_handler(commands=["test"])
def start_message(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text="Три", callback_data=3))
    markup.add(telebot.types.InlineKeyboardButton(text="Четыре", callback_data=4))
    markup.add(telebot.types.InlineKeyboardButton(text="Пять", callback_data=5))
    bot.send_message(message.chat.id, text="Смотри что умею!", reply_markup=markup)


@bot.message_handler(commands=["weather"])
def start_message(message):
    latitude = 55.75
    longitude = 37.6
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true&hourly=temperature_2m,relativehumidity_2m,windspeed_10m"
    try:
        r = requests.get(url)
        meta = json.loads(r.text)["current_weather"]
        text = f"Сейчас в Москве {meta['temperature']} °C\nСкорость ветра {(meta['windspeed'] / 3.6):.2f} м/с"
    except:
        text = "Что-то пошло не так"
    bot.send_message(message.chat.id, text=text)


@bot.message_handler(content_types=["text"])
def get_text_messages(message):

    if message.text == "👋 Поздороваться":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # создание новых кнопок
        btn1 = types.KeyboardButton("Как стать автором на Хабре?")
        btn2 = types.KeyboardButton("Правила сайта")
        btn3 = types.KeyboardButton("Советы по оформлению публикации")
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.from_user.id, "❓ Задайте интересующий вас вопрос", reply_markup=markup)  # ответ бота

    elif message.text == "Как стать автором на Хабре?":
        bot.send_message(
            message.from_user.id,
            "Вы пишете первый пост, его проверяют модераторы, и, если всё хорошо, отправляют в основную ленту Хабра, где он набирает просмотры, комментарии и рейтинг. В дальнейшем премодерация уже не понадобится. Если с постом что-то не так, вас попросят его доработать.\n \nПолный текст можно прочитать по "
            + "[ссылке](https://habr.com/ru/sandbox/start/)",
            parse_mode="Markdown",
        )

    elif message.text == "Правила сайта":
        bot.send_message(
            message.from_user.id,
            "Прочитать правила сайта вы можете по " + "[ссылке](https://habr.com/ru/docs/help/rules/)",
            parse_mode="Markdown",
        )

    elif message.text == "Советы по оформлению публикации":
        bot.send_message(
            message.from_user.id,
            "Подробно про советы по оформлению публикаций прочитать по "
            + "[ссылке](https://habr.com/ru/docs/companies/design/)",
            parse_mode="Markdown",
        )


bot.polling(none_stop=False, interval=0)  # обязательная для работы бота часть
