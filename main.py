import os
import logging.config

from log_settings import logger_config
from dotenv import load_dotenv, find_dotenv
import telebot

logging.config.dictConfig(logger_config)

logger = logging.getLogger("bot_logger")

load_dotenv(find_dotenv())

TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(content_types=["text"])
def echo_message(message):
    logger.info("Echo message")
    bot.send_message(message.chat.id, message.text)


bot.polling()
