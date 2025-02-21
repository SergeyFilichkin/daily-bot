from datetime import datetime, timedelta
from os import getenv

from gspread import authorize
from oauth2client.service_account import ServiceAccountCredentials
import logging

DOCUMENT_ID = getenv("DOCUMENT_ID")
ALL_STUDENTS = "Ученики"

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json", scope
)  # TODO: use gspread instead oauth2client
gc = authorize(credentials)
sheet = gc.open_by_key(DOCUMENT_ID)

logger_sheets = logging.getLogger('google_sheets')


def initialize_students_sheet() -> None:
    header = ("Telegram ID", "Имя", "Фамилия", "Часы")
    create_sheet_with_header(ALL_STUDENTS, header)


def create_individual_sheet(telegram_id: int, surname: str) -> None:
    student = f"{surname}_{telegram_id}"
    header = ("Дата", "Запланированные темы", "Изученные темы", "Часы")
    create_sheet_with_header(student, header)


def add_student(
    telegram_id: int, name: str, surname: str, daily_tracking: bool
) -> None:
    if not is_all_students_sheet_exists():
        initialize_students_sheet()
    worksheet = sheet.worksheet(ALL_STUDENTS)
    worksheet.append_row((telegram_id, name, surname, daily_tracking))
    create_individual_sheet(telegram_id, surname)


def write_weekly_study_plan(telegram_id: int, surname: str, topics: str) -> None:
    monday = datetime.now().strftime("%d.%m")
    sunday = (datetime.now() + timedelta(days=6)).strftime("%d.%m")
    worksheet = sheet.worksheet(f"{surname}_{telegram_id}")
    logger_sheets.debug(f'write_weekly_study_plan to {surname}_{telegram_id}')
    worksheet.append_row((f"{monday} - {sunday}", topics))


def write_daily_progress(
    telegram_id: int,
    surname: str,
    completed_topics: str,
    hours: int | None = None,
) -> None:
    current_date = datetime.now().strftime("%d.%m")
    worksheet = sheet.worksheet(f"{surname}_{telegram_id}")
    logger_sheets.debug(f'write_daily_progress to {surname}_{telegram_id}')
    worksheet.append_row((current_date, "", completed_topics, hours or ""))


def get_student_data_by_telegram_id(telegram_id: int) -> dict[str, str]:
    if not is_all_students_sheet_exists():
        initialize_students_sheet()
    worksheet = sheet.worksheet(ALL_STUDENTS)
    rows = worksheet.get_all_values()

    for row in rows:
        if row[0] == str(telegram_id):
            telegram_id, name, surname, daily_tracking = row
            logger_sheets.info(f'Данные о пользователе {telegram_id}, {name}, {surname}, {daily_tracking}')
            return {
                "telegram id": telegram_id,
                "name": name,
                "surname": surname,
                "daily tracking": daily_tracking,
            }


def get_all_students_ids() -> list[str]:
    if not is_all_students_sheet_exists():
        initialize_students_sheet()
    worksheet = sheet.worksheet(ALL_STUDENTS)
    ids = worksheet.col_values(1)[1:]
    logger_sheets.warning(f'{str([(get_student_data_by_telegram_id(int(id))) for id in ids])}')
    return ids


def is_all_students_sheet_exists() -> bool:
    worksheets_names = {worksheet.title for worksheet in sheet.worksheets()}
    return ALL_STUDENTS in worksheets_names

def create_sheet_with_header(sheet_name: str, header: tuple) -> None:
    sheet.add_worksheet(title=sheet_name, rows="10000", cols="5")
    worksheet = sheet.worksheet(sheet_name)
    worksheet.append_row(header)
    worksheet.format("A1:D1", {"textFormat": {"bold": True}})
