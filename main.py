import os

from dotenv import load_dotenv, find_dotenv
import telebot

load_dotenv(find_dotenv())

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(content_types=["text"])
def echo_message(message):
    bot.send_message(message.chat.id, message.text)


bot.polling()
