from telebot.handler_backends import State, StatesGroup


class UserRegistration(StatesGroup):
    get_telegram_id = State()
    get_name_and_surname = State()
    confirm_daily_time_tracking = State()


class UserProgress(StatesGroup):
    set_weekly_study_plan = State()
    log_daily_progress = State()
    log_daily_study_hours = State()
