import logging


class FileHandler(logging.Handler):
    def __init__(self, filename):
        logging.Handler.__init__(self)
        self.filename = filename

    def emit(self, record):
        message = self.format(record)
        with open(self.filename, "a") as file:
            file.write(message + "\n")
class LevelFileHandler(logging.Handler):
    def __init__(self, filename, mode):
        super().__init__()
        self.filename = filename
        self.mode = mode
    def emit(self, record: logging.LogRecord):
        message: str = self.format(record)
        level = record.levelname.lower()
        filename = self.filename + level + '.log'
        with open(filename, mode=self.mode) as f:
            f.write(message + '\n')

logger_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "std_format": {
            "format": "{asctime} - {levelname} - {name} - {message}",
            "style": "{",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "std_format",
        },
        "file": {
                "()": lambda: FileHandler('bot.log'),
                "level": "INFO",
                "formatter": "std_format",
            },
        "level_files_notifications": {
            "()": lambda: LevelFileHandler('notifications', mode='a'),
            "level": "DEBUG",
            "formatter": "std_format",
        },
        "level_files_google_sheets": {
            "()": lambda: LevelFileHandler('google_sheets', mode='a'),
            "level": "DEBUG",
            "formatter": "std_format",
        },
    },
    "loggers": {
        "bot_logger": {
            "level": "INFO",
            "handlers": ["console", "file"],
        },
        "notifications": {
            "level": "DEBUG",
            "handlers": ["console", "level_files_notifications"],
        },
        "google_sheets": {
            "level": "DEBUG",
            "handlers": ["console", "level_files_google_sheets"],
        }
    },
}
