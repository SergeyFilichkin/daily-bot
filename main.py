import logging.config
from os import getenv

from telebot import TeleBot, custom_filters
from telebot.states.sync.middleware import StateMiddleware
from telebot.storage import StateRedisStorage

from handlers import register_handlers
from log_settings import logger_config
from notifications import schedule_all_notifications, scheduler

TOKEN = getenv("TOKEN")

logging.config.dictConfig(logger_config)
logger = logging.getLogger("bot_logger")

state_storage = StateRedisStorage()  # TODO: change to redis

bot = TeleBot(TOKEN, state_storage=state_storage, use_class_middlewares=True)
bot.setup_middleware(StateMiddleware(bot))
bot.add_custom_filter(custom_filters.StateFilter(bot))

scheduler.start()
schedule_all_notifications(bot)

register_handlers(bot)


if __name__ == "__main__":
    logger.warning('start bot')
    bot.infinity_polling()
