import gspread

gc = gspread.service_account()

daily_table = "Daily-bot"

sh = gc.open(daily_table)


def create_list_student_sheet():
    """Создает лист со списком учеников."""
    sheet = sh.add_worksheet(title="Ученики", rows=1000, cols=26)

    sheet.batch_update(
        [
            {
                "range": "A1:D1",
                "values": [["Телеграм_id", "Имя", "Фамилия", "Учет часов"]],
            }
        ]
    )

    sheet.format("A1:D1", {"textFormat": {"bold": True}})

    return sheet


def create_personal_student_sheet(telegram_id, surname):
    """Создает персональный лист ученика."""
    title = f"{telegram_id}_{surname}"
    sheet = sh.add_worksheet(title=title, rows=1000, cols=26)

    sheet.batch_update(
        [
            {
                "range": "A1:D1",
                "values": [
                    ["Дата", "Запланированные темы", "Изученные темы", "Часы"]
                ],
            }
        ]
    )

    sheet.format("A1:D1", {"textFormat": {"bold": True}})

    return sheet


def add_student(telegram_id, name, surname, hours):
    """
    Добавление ученика в список учеников и создание персонального листа ученика.
    Функция проверяет есть ли лист 'Ученики', если есть добавляет в список и создает персональный лист,
    если нет сначала создает список 'Ученики'.

    В блоке except используется функция create_list_student_sheet().
    В блоке finally используется функция create_personal_student_sheet(telegram_id, surname).
    """
    try:
        sh.worksheet("Ученики")

    except gspread.WorksheetNotFound:
        create_list_student_sheet()

    finally:
        ws = sh.worksheet("Ученики")
        values = ws.col_values(1)

        first_empty_row = len(values) + 1

        ws.batch_update(
            [
                {
                    "range": f"A{first_empty_row}:D{first_empty_row}",
                    "values": [[telegram_id, name, surname, hours]],
                }
            ]
        )

        create_personal_student_sheet(telegram_id, surname)


def add_week_topics(telegram_id, surname, date, topics):
    """Добавляет дату и список дел на неделю"""
    ws = sh.worksheet(f"{telegram_id}_{surname}")
    values = ws.col_values(1)

    first_empty_row = len(values) + 1

    ws.batch_update(
        [
            {
                "range": f"A{first_empty_row}:B{first_empty_row}",
                "values": [[date, topics]],
            }
        ]
    )


def add_daily_progress(telegram_id, surname, date, topics, hours):
    """Фиксирует прогресс за день"""
    ws = sh.worksheet(f"{telegram_id}_{surname}")
    values = ws.col_values(1)

    first_empty_row = len(values) + 1

    ws.batch_update(
        [
            {"range": f"A{first_empty_row}", "values": [[date]]},
            {
                "range": f"C{first_empty_row}:D{first_empty_row}",
                "values": [[topics, hours]],
            },
        ]
    )


def get_all_telegram_id():
    """ "Получение списка всех Tелеграм_ID"""
    ws = sh.worksheet("Ученики")
    values_list = ws.col_values(1)
    return values_list
