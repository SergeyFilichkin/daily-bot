import gspread
from typing import Union

gc = gspread.service_account()

daily_table = "Daily-bot"

sh = gc.open(daily_table)


def create_sheets(values: list, title: str):
    """Создает листы."""
    sheet = sh.add_worksheet(title=title, rows=1000, cols=26)
    values = sheet.batch_update(
        [
            {
                "range": "A1:D1",
                "values": values,
            }
        ]
    )

    sheet.format("A1:D1", {"textFormat": {"bold": True}})

    return values


def add_values(
    title: str, a: Union[str, int] = "", b: str = "", c: str = "", d: str = ""
):
    """Добавляет значения."""
    ws = sh.worksheet(title)
    values = ws.col_values(1)
    first_empty_row = len(values) + 1

    ws.batch_update(
        [
            {
                "range": f"A{first_empty_row}:D{first_empty_row}",
                "values": [[a, b, c, d]],
            }
        ]
    )

    return values


def create_list_student_sheet():
    """Создает лист со списком учеников."""
    title = "Ученики"
    vals = [["Дата", "Запланированные темы", "Изученные темы", "Часы"]]

    create_sheets(vals, title)


def create_personal_student_sheet(telegram_id: int, surname: str):
    """Создает персональный лист ученика."""
    title = f"{telegram_id}_{surname}"
    vals = [["Дата", "Запланированные темы", "Изученные темы", "Часы"]]

    create_sheets(vals, title)


def add_student(telegram_id: int, name: str, surname: str, hours: str):
    """
    Добавление ученика в список учеников и создание персонального листа ученика.
    Функция проверяет есть ли лист 'Ученики', если есть добавляет в список и создает персональный лист,
    если нет сначала создает список 'Ученики'.
    """
    title = "Ученики"
    a = telegram_id
    b = name
    c = surname
    d = hours

    try:
        sh.worksheet(title)

    except gspread.WorksheetNotFound:
        create_list_student_sheet()

    finally:
        add_values(title, a, b, c, d)

        create_personal_student_sheet(telegram_id, surname)


def add_week_topics(telegram_id: int, surname: str, date: str, topics: str):
    """Добавляет дату и список дел на неделю"""
    title = f"{telegram_id}_{surname}"
    a = date
    b = topics

    add_values(title, a, b)


def add_daily_progress(
    telegram_id: int, surname: str, date: str, topics: str, hours: str
):
    """Фиксирует прогресс за день"""
    title = f"{telegram_id}_{surname}"
    a = date
    b = ""
    c = topics
    d = hours

    add_values(title, a, b, c, d)


def get_all_telegram_id():
    """Получение списка всех Tелеграм_ID"""
    ws = sh.worksheet("Ученики")
    values_list = ws.col_values(1)
    return values_list
