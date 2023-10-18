from switchbot.config import get_switchbot_key_pair
from switchbot.adapters.iot_api_server import SwitchBotApiServer
from switchbot.domain.model import SwitchBotDevice, SwitchBotStatus


def test_switchbotapi():
    secret, token = get_switchbot_key_pair()
    switchbotapi = SwitchBotApiServer()
    """測試 get_dev_list API"""
    dev_list = switchbotapi.get_dev_list(secret=secret, token=token)
    assert dev_list
    assert len(dev_list) > 0
    dev = dev_list[0]
    assert isinstance(dev, SwitchBotDevice)
    dev_id = dev.device_id
    """測試 get_dev_status API"""
    dev_status = switchbotapi.get_dev_status(secret=secret, token=token, dev_id=dev_id)
    assert isinstance(dev_status, SwitchBotStatus)
    assert dev_status.device_id == dev_id
