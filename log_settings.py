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
    def __init__(self, filename):
        logging.Handler.__init__(self)
        self.filename = filename

    def emit(self, record):
        message = self.format(record)
        level = record.levelname.lower()
        filename = level + self.filename
        with open(filename, "a") as file:
            file.write(message + "\n")

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
            "()": FileHandler,
            "level": "INFO",
            "filename": "bot.log",
            "formatter": "std_format",
        },
        "level_files": {
            "()": LevelFileHandler,
            "level": "DEBUG",
            "filename": "notification.log",
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
            "handlers": ["console", "file", "level_files"],
        }
    },
}
