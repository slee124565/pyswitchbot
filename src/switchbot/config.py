import os
import dotenv

dotenv.load_dotenv()


def get_switchbot_key_pair():
    secret = os.getenv('SWITCHBOTAPI_SECRET_KEY')
    token = os.getenv('SWITCHBOTAPI_TOKEN')
    return secret, token


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
            "level": "INFO"
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
        # "switchbot.adapters.switchbotapi": {
        #     "handlers": ["console"],
        #     "level": "DEBUG",
        #     "propagate": False
        # }
    }
}
