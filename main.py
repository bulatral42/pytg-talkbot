"""Telegram bot 'Balabobny pomogator' for simple daily tasks."""

import json
import logging
import os
from collections import defaultdict
from enum import Enum

import requests
import telebot
from telebot import types


class BotState(Enum):
    Base = 1
    BobaChat = 2
    MakeRemember = 3


class ChatState:
    def __init__(self):
        self._state = BotState.Base

    def set_state(self, state: BotState):
        self._state = state

    def get_state(self) -> BotState:
        return self._state


bot_token = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(bot_token)
chat_db = defaultdict(ChatState)

menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=12)
menu_markup.add(types.KeyboardButton("Поболтать :)"))
menu_markup.add(types.KeyboardButton("Погода в Москве"))
menu_markup.add(types.KeyboardButton("Сделать напоминание TODO"))


def request_model(context):
    request_failed = False
    try:
        r = requests.post(
            url=os.environ.get("MODEL_URL"),
            json={"Context": [context + " [SEP]"]},
        )
    except:
        request_failed = True
    if request_failed:
        return None
    max_tokens = 0
    response_text = ""
    for response in json.loads(r.text)["Responses"]:
        if response["NumTokens"] > max_tokens:
            max_tokens = response["NumTokens"]
            response_text = response["Response"]
    return response_text


@bot.message_handler(commands=["start"])
def start(message):
    """Welcome user of Bot."""
    chat_db[message.chat.id].set_state(BotState.Base)
    bot.send_message(
        message.chat.id,
        f"👋 Привет, {message.from_user.first_name}! Я твой бот-помошник Балабобик!",
        reply_markup=menu_markup,
    )


@bot.message_handler(commands=["chat"])
@bot.message_handler(func=lambda msg: msg.text == "Поболтать :)" and chat_db[msg.chat.id].get_state() == BotState.Base)
def start_chat(message):
    logging.debug("Start chatting")
    chat_db[message.chat.id].set_state(BotState.BobaChat)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=12)
    markup.add(types.KeyboardButton("Stop Чат"))
    bot.send_message(message.chat.id, text="Что ж, давайте поговорим", reply_markup=markup)


@bot.message_handler(func=lambda msg: chat_db[msg.chat.id].get_state() == BotState.BobaChat)
def message_with_boba(message):
    if message.text == "Stop Чат":
        end_chat(message)
    else:
        bot.send_message(message.chat.id, text=request_model(message.text))


def end_chat(message):
    logging.debug("End chatting")
    chat_db[message.chat.id].set_state(BotState.Base)

    bot.send_message(
        message.chat.id,
        f"Cпасибо за приятный разговор!)",
        reply_markup=menu_markup,
    )


@bot.message_handler(commands=["weather"])
@bot.message_handler(
    func=lambda msg: msg.text == "Погода в Москве" and chat_db[msg.chat.id].get_state() == BotState.Base
)
def get_moscow_weather(message):
    """Show weather forecast.

    Current weather in Moscow from open-meteo.com site.
    """
    logging.debug("Calling weather API")
    latitude = 55.75
    longitude = 37.6
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true&hourly=temperature_2m,relativehumidity_2m,windspeed_10m"
    try:
        r = requests.get(url)
        meta = json.loads(r.text)["current_weather"]
        text = f"Сейчас в Москве {meta['temperature']} °C\nСкорость ветра {(meta['windspeed'] / 3.6):.2f} м/с"
    except:
        text = "Что-то пошло не так"
    chat_db[message.chat.id].set_state(BotState.Base)
    bot.send_message(message.chat.id, text=text)


logging.basicConfig(level=logging.DEBUG, format=" %(asctime)s - %(levelname)s - %(message)s")

bot.infinity_polling(restart_on_change=True)
