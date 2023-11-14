import logging
import pytest
import time
import requests
from pathlib import Path
import logging.config as logging_config
from tenacity import retry, stop_after_delay
from switchbot import config

logging_config.dictConfig(config.logging_config)
logger = logging.getLogger(__name__)


@retry(stop=stop_after_delay(10))
def wait_for_webapp_to_come_up():
    return requests.get(config.get_api_url())


@pytest.fixture
def restart_api():
    (Path(__file__).parent / "../src/switchbot/entrypoints/flask_app.py").touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()


@pytest.fixture(scope="class")
def setup_subscrb_user():
    """todo"""
    logger.info(f'setup test users for subscription')
    users = ['user1', 'user2', 'user3']
    yield users
    logger.info(f'teardown test users for subscription')
