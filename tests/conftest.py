import logging
import pytest
import time
import os
import requests
import dotenv
from pathlib import Path
import logging.config as logging_config
from tenacity import retry, stop_after_delay
from switchbot import config

dotenv.load_dotenv()
logging_config.dictConfig(config.logging_config)
logger = logging.getLogger(__name__)


@retry(stop=stop_after_delay(10))
def wait_for_webapp_to_come_up():
    return requests.get(config.get_api_uri())


@pytest.fixture
def restart_api():
    logger.info(f'restart_api fixture called')
    if os.path.exists('.datastore'):
        os.remove('.datastore')
    (Path(__file__).parent / "../src/switchbot/entrypoints/flask_app.py").touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()
