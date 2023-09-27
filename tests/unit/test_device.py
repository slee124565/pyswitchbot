from switchbot.domain.model import SwitchBotDevice


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
