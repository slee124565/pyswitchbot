import logging
from switchbot.domain.model import SwitchBotDevice, SwitchBotStatus, SwitchBotScene, SwitchBotUserRepo

logger = logging.getLogger(__name__)
_dev_plug_mini_CFD2 = {
    'deviceId': '6055F92FCFD2',
    'deviceName': '小風扇開關',
    'deviceType': 'Plug Mini (US)',
    'enableCloudService': True,
    'hubDeviceId': ''
}
_state_plug_mini_CFD2 = {
    "deviceId": "6055F92FCFD2",
    "deviceType": "Plug Mini (US)",
    "hubDeviceId": "6055F92FCFD2",
    "power": "off",
    "version": "V1.4-1.4",
    "voltage": 114.7,
    "weight": 0.0,
    "electricityOfDay": 3,
    "electricCurrent": 0.0
}
_dev_plug_mini_FF22 = {
    "deviceId": "6055F930FF22",
    "deviceName": "風扇開關",
    "deviceType": "Plug Mini (US)",
    "enableCloudService": True,
    "hubDeviceId": ""
}
_state_plug_mini_FF22 = {
    "deviceId": "6055F930FF22",
    "deviceType": "Plug Mini (US)",
    "hubDeviceId": "6055F930FF22",
    "power": "off",
    "version": "V1.4-1.4",
    "voltage": 114.7,
    "weight": 0.0,
    "electricityOfDay": 122,
    "electricCurrent": 0.0
}
_dev_motion_sensor_CDA5 = {
    'deviceId': 'C395D0F0CDA5',
    'deviceName': 'Motion Sensor A5',
    'deviceType': 'Motion Sensor',
    'enableCloudService': False,
    'hubDeviceId': ''
}


def test_switchbot_device_schema():
    for data in [_dev_plug_mini_CFD2, _dev_motion_sensor_CDA5]:
        obj = SwitchBotDevice.load(data)
        assert isinstance(obj, SwitchBotDevice)
        assert obj.device_id == data.get('deviceId')
        assert obj.device_name == data.get('deviceName')
        assert obj.device_type == data.get('deviceType')
        assert obj.enable_cloud_service == data.get('enableCloudService')
        assert obj.hub_device_id == data.get('hubDeviceId')
        assert obj.dump() == data


def test_switchbot_status_schema():
    for data in [_state_plug_mini_CFD2, _state_plug_mini_FF22]:
        obj = SwitchBotStatus.load(data)
        assert isinstance(obj, SwitchBotStatus)
        assert obj.device_id == data.get('deviceId')
        assert obj.device_type == data.get('deviceType')
        assert obj.hub_device_id == data.get('hubDeviceId')
        assert obj.power == data.get('power')
        assert obj.voltage == data.get('voltage')
        assert obj.weight == data.get('weight')
        assert obj.electricity_of_day == data.get('electricityOfDay')
        assert obj.electric_current == data.get('electricCurrent')
        assert obj.version == data.get('version')
        assert obj.dump() == data


def test_switchbot_scene_schema():
    data = {
        "sceneId": "T01-202309291436-01716250",
        "sceneName": "allOff"
    }
    obj = SwitchBotScene.load(data)
    assert isinstance(obj, SwitchBotScene)
    assert obj.scene_id == data.get('sceneId')
    assert obj.scene_name == data.get('sceneName')
    assert obj.dump() == data


def test_switchbot_user_repo_schema():
    data = {
        'userId': 'user_id',
        'devices': [_dev_plug_mini_CFD2, _dev_plug_mini_FF22],
        'states': [_state_plug_mini_CFD2, _state_plug_mini_FF22],
        'scenes': [],
        'webhooks': []
    }
    obj = SwitchBotUserRepo.load(data)
    logger.info(f'{type(obj)}')
    assert isinstance(obj, SwitchBotUserRepo)
    assert obj.user_id == 'user_id'
    assert len(obj.devices) == 2
    assert obj.dump() == data
