logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
        'standard': {
            'format': '[%(levelname)s] %(name)s: %(message)s'
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "DEBUG"
        }
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO"
    },
    "loggers": {
        "requests": {
            "level": "INFO"
        },
        "switchbot.adapters.switchbotapi": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False
        }
    }
}
