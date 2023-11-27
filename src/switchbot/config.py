import os
import dotenv

dotenv.load_dotenv()


def get_api_url():
    host = os.environ.get("API_HOST", "127.0.0.1")
    port = 5000 if host == "127.0.0.1" else 80
    return f"http://{host}:{port}"


def get_switchbot_key_pair():
    secret = os.getenv('SWITCHBOTAPI_SECRET_KEY')
    token = os.getenv('SWITCHBOTAPI_TOKEN')
    return secret, token


def get_postgres_uri():
    host = os.environ.get("DB_HOST", "localhost")
    port = 54321 if host == "localhost" else 5432
    password = os.environ.get("DB_PASSWORD", "abc123")
    user, db_name = "allocation", "allocation"
    return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"


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
            # 'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "DEBUG",
            # "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "simple",
            "filename": "switchbotapi.log",
            "maxBytes": 5 * 1024 * 1024,  # 5 MB
            "backupCount": 3,
            "level": "INFO"
        }
    },
    "root": {
        "handlers": ["console"],
    },
    "loggers": {
        "urllib3": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False
        },
        "werkzeug": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False
        },
        "switchbot": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False
        },
        # "switchbot.adapters.iot_api_server": {
        #     "handlers": ["console", "file"],
        #     "level": "WARNING",
        #     "propagate": False
        # },
        "tests": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False
        }
    }
}
