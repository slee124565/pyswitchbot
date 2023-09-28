from switchbot.domain.model import SwitchBotDevice, SwitchBotStatus


def test_load_switchbot_device_from_json():
    data = {
        'deviceId': '6055F92FCFD2',
        'deviceName': '小風扇開關',
        'deviceType': 'Plug Mini (US)',
        'enableCloudService': True,
        'hubDeviceId': ''
    }
    obj = SwitchBotDevice.fromdict(data)
    assert isinstance(obj, SwitchBotDevice)
    assert obj.device_id == data.get('deviceId')
    assert obj.device_name == data.get('deviceName')
    assert obj.device_type == data.get('deviceType')
    assert obj.enable_cloud_service == data.get('enableCloudService')
    assert obj.hub_device_id == data.get('hubDeviceId')
    assert obj.asdict() == data


def test_switchbot_state_model():
    data = {
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
    obj = SwitchBotStatus.fromdict(data)
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
    assert obj.asdict() == data
