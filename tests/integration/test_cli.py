"""todo: how to test cli tool?
1. bootstrap inject with AbstractXataAPI and AbstractIotAPI (SwitchBot OpenAPI)
2. pytest trigger click-based object, cli.switchbotcli
"""
import pytest
import logging
from switchbot import config
from switchbot.entrypoints.cli import switchbotcli
from click.testing import CliRunner

env_secret, env_token = config.get_switchbot_key_pair()
logger = logging.getLogger(__name__)


def test_auth_check():
    runner = CliRunner()
    args = f"auth check --secret {env_secret} --token {env_token}".split(" ")
    result = runner.invoke(switchbotcli, args)
    logger.info(f"return code {result.exit_code}")
    logger.info(f"return output {result.output}")
