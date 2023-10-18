"""
cmd_resp_status = {
        'isDelay': False,
        'rssiQuality': 54,
        'currentElectricity': 0,
        'currentTemperature': 73,
        'onTime': 43,
        'currentWeight': 20,
        'currentPower': 0,
        'isOverload': False,
        'currentVoltage': 1122,
        'power': 'off',
        'isLed': True
    }
"""
from switchbot.domain.model import SwitchBotDevice, SwitchBotStatus, SwitchBotScene


def test_switchbot_device_schema():
    data_plug_min = {
        'deviceId': '6055F92FCFD2',
        'deviceName': '小風扇開關',
        'deviceType': 'Plug Mini (US)',
        'enableCloudService': True,
        'hubDeviceId': ''
    }
    data_motion_sensor = {
        'deviceId': 'C395D0F0CDA5',
        'deviceName': 'Motion Sensor A5',
        'deviceType': 'Motion Sensor',
        'enableCloudService': False,
        'hubDeviceId': ''
    }
    for data in [data_plug_min, data_motion_sensor]:
        obj = SwitchBotDevice.load(data)
        assert isinstance(obj, SwitchBotDevice)
        assert obj.device_id == data.get('deviceId')
        assert obj.device_name == data.get('deviceName')
        assert obj.device_type == data.get('deviceType')
        assert obj.enable_cloud_service == data.get('enableCloudService')
        assert obj.hub_device_id == data.get('hubDeviceId')
        assert SwitchBotDevice.dump(obj) == data


def test_switchbot_status_schema():
    data_plug_mini = {
        "deviceId": "6055F92FCFD2",
        "deviceType": "Plug Mini (US)",
        "hubDeviceId": "6055F92FCFD2",
        "power": "off",
        "voltage": 114.1,
        "weight": 0,
        "electricityOfDay": 3,
        "electricCurrent": 0,
        "version": "V1.4-1.4"
    }
    data_motion_sensor = {
        'deviceId': 'C395D0F0CDA5',
        'deviceType': 'Motion Sensor',
        'hubDeviceId': 'C8D8E9A17ED3',
        'moveDetected': False,
        'brightness': 'dim',
        'version': 'V1.3',
        'battery': 100
    }
    for data in [data_plug_mini, data_motion_sensor]:
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
        assert SwitchBotStatus.dump(obj) == data


def test_switchbot_scene_schema():
    data = {
        "sceneId": "T01-202309291436-01716250",
        "sceneName": "allOff"
    }
    obj = SwitchBotScene.load(data)
    assert isinstance(obj, SwitchBotScene)
    assert obj.scene_id == data.get('sceneId')
    assert obj.scene_name == data.get('sceneName')
    assert SwitchBotScene.dump(obj) == data
