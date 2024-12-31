from os import getenv

from telebot import TeleBot
from telebot.apihelper import ApiException
from telebot.states.sync.context import StateContext
from telebot.types import Message

from google_sheets import (
    add_student,
    get_student_data_by_telegram_id,
    write_daily_progress,
    write_weekly_study_plan,
)
from notifications import add_daily_progress_job, add_weekly_study_plan_job
from states import UserProgress, UserRegistration

CHAT_ID = getenv("CHAT_ID")


def register_handlers(bot: TeleBot) -> None:
    @bot.message_handler(commands=["start"])
    def handle_start(message: Message, state: StateContext) -> None:
        telegram_id = message.from_user.id
        data = get_student_data_by_telegram_id(telegram_id)
        if data:
            bot.send_message(
                telegram_id,
                f"Вы уже зарегистрированы. Ваши данные:\n"
                f"Telegram ID:   {telegram_id}\n"
                f"Имя:   {data['name']}\n"
                f"Фамилия:   {data['surname']}\n"
                f"Учет часов:   {data['daily tracking']}",
            )
            return

        # TODO: Add to README that the bot must be in the chat for this to work.
        try:
            user = bot.get_chat_member(CHAT_ID, telegram_id)
            if user.status in ("left", "kicked"):
                bot.send_message(
                    telegram_id,
                    "Этот бот предназначен для участников закрытого сообщетва "
                    "волков-квадробоберов. Если ты не один из нас, то "
                    "пожалуйста, уйди отсюда и больше никогда не приходи",
                )
                return

        except ApiException:
            # TODO: Add to logs that the exception is raised when the bot is not added to the chat
            pass

        state.set(UserRegistration.get_telegram_id)
        state.add_data(telegram_id=telegram_id)
        state.set(UserRegistration.get_name_and_surname)
        bot.send_message(
            message.chat.id,
            "Привет! Я - бот для отслеживания прогресса в обучении. Для "
            "регистрации, пожалуйста, введите свои имя и фамилию в одну строку "
            "через пробел",
        )

    @bot.message_handler(state=UserRegistration.get_name_and_surname)
    def get_name_and_surname(message: Message, state: StateContext) -> None:
        name, surname = message.text.strip().title().split()
        state.add_data(name=name, surname=surname)
        state.set(UserRegistration.confirm_daily_time_tracking)
        bot.send_message(
            message.chat.id,
            "Требуется ли вести ежедневный учет часов, потраченных на обучение?"
            "\nВведите 'да' или 'нет'",
        )

    @bot.message_handler(state=UserRegistration.confirm_daily_time_tracking)
    def confirm_daily_time_tracking(message: Message, state: StateContext) -> None:
        message_text = message.text.strip().lower()
        daily_tracking = message_text == "да"
        with state.data() as data:
            telegram_id = data.get("telegram_id")
            name = data.get("name")
            surname = data.get("surname")
        state.delete()
        add_student(telegram_id, name, surname, daily_tracking)
        add_weekly_study_plan_job(bot, telegram_id)
        add_daily_progress_job(bot, telegram_id)
        bot.send_message(
            message.chat.id,
            "Регистрация прошла успешно! Ваши данные:\n"
            f"Telegram ID:   {telegram_id}\n"
            f"Имя:   {name}\n"
            f"Фамилия:   {surname}\n"
            f"Учет часов:   {daily_tracking}",
        )

    @bot.message_handler(state=UserProgress.set_weekly_study_plan)
    def set_weekly_study_plan(message: Message, state: StateContext) -> None:
        data = get_student_data_by_telegram_id(message.from_user.id)
        write_weekly_study_plan(
            data["telegram id"], data["surname"], message.text.strip()
        )
        state.delete()
        bot.send_message(
            data["telegram id"],
            "План изучения сохранен. Удачной и плодотворной недели!",
        )

    @bot.message_handler(state=UserProgress.log_daily_progress)
    def log_daily_progress(message: Message, state: StateContext) -> None:
        studied_topics = message.text.strip()
        data = get_student_data_by_telegram_id(message.from_user.id)
        if data["daily tracking"] == "FALSE":
            write_daily_progress(data["telegram id"], data["surname"], studied_topics)
            state.delete()
            bot.send_message(data["telegram id"], "Данные сохранены")
            return

        state.add_data(
            telegram_id=data["telegram id"],
            surname=data["surname"],
            daily_progress=studied_topics,
        )
        state.set(UserProgress.log_daily_study_hours)
        bot.send_message(
            message.chat.id,
            "Сколько часов вы потратили на обучение? При необходимости, "
            "округлите до целого числа по своему усмотрению",
        )

    @bot.message_handler(state=UserProgress.log_daily_study_hours)
    def log_daily_study_hours(message: Message, state: StateContext) -> None:
        with state.data() as data:
            telegram_id = data.get("telegram_id")
            surname = data.get("surname")
            studied_topics = data.get("daily_progress")
        hours = message.text.strip()
        write_daily_progress(telegram_id, surname, studied_topics, hours)
        state.delete()
        bot.send_message(telegram_id, "Данные сохранены c учетом потраченных часов")
