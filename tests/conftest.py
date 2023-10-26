import pytest
import time
import requests
from pathlib import Path
from switchbot import config
from tenacity import retry, stop_after_delay


@retry(stop=stop_after_delay(10))
def wait_for_webapp_to_come_up():
    return requests.get(config.get_api_url())


@pytest.fixture
def restart_api():
    (Path(__file__).parent / "../src/switchbot/entrypoints/flask_app.py").touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()
