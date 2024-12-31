from apscheduler.schedulers.background import BackgroundScheduler
from telebot import TeleBot

from google_sheets import get_all_students_ids
from states import UserProgress

scheduler = BackgroundScheduler(timezone="Europe/Moscow")

WEEKLY_JOB_TIME = "thu, 17:20"
DAILY_JOB_TIME = "17:22"


def send_weekly_study_plan(bot: TeleBot, telegram_id: int) -> None:
    bot.set_state(telegram_id, UserProgress.set_weekly_study_plan)
    bot.send_message(
        telegram_id,
        "Направьте список тем, которые Вы планируете изучить в течение недели."
        " В качестве разделителя используйте ; (точка с запятой), например:"
        " Итераторы; Генераторы; Декораторы; Мелиораторы; Механизаторы",
    )


def send_daily_progress(bot: TeleBot, telegram_id: int) -> None:
    bot.set_state(telegram_id, UserProgress.log_daily_progress)
    bot.send_message(
        telegram_id,
        "Перечислите изученные за день темы, используя в качестве разделителя"
        " ; (точку с запятой), например: Итераторы; Генераторы",
    )


def add_weekly_study_plan_job(bot: TeleBot, telegram_id: int) -> None:
    job_id = f"weekly_{telegram_id}"
    day, time = WEEKLY_JOB_TIME.split(", ")
    hour, minute = time.split(":")

    scheduler.add_job(
        func=send_weekly_study_plan,
        trigger="cron",
        day_of_week=day,
        hour=hour,
        minute=minute,
        id=job_id,
        kwargs={"bot": bot, "telegram_id": telegram_id},
    )


def add_daily_progress_job(bot: TeleBot, telegram_id: int) -> None:
    job_id = f"daily_{telegram_id}"
    hour, minute = DAILY_JOB_TIME.split(":")

    scheduler.add_job(
        func=send_daily_progress,
        trigger="cron",
        hour=hour,
        minute=minute,
        id=job_id,
        kwargs={"bot": bot, "telegram_id": telegram_id},
    )


def schedule_all_notifications(bot: TeleBot) -> None:
    ids = get_all_students_ids()
    for id in ids:
        add_weekly_study_plan_job(bot, id)
        add_daily_progress_job(bot, id)
