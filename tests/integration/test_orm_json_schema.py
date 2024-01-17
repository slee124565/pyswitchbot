import logging

# import switchbot.domain.model
# from switchbot.adapters import file_datastore
from switchbot.domain import model

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
_change_plug_mini_FF22 = {
    "eventType": "changeReport",
    "eventVersion": "1",
    "context": {
        "deviceType": "WoPlugUS",
        "deviceMac": "6055F930FF22",
        "powerState": "ON",
        "timeOfSample": 1698720698088
    }
}
_dev_motion_sensor_CDA5 = {
    'deviceId': 'C395D0F0CDA5',
    'deviceName': 'Motion Sensor A5',
    'deviceType': 'Motion Sensor',
    'enableCloudService': False,
    'hubDeviceId': ''
}
_dev_wo_sweeper_mini = {
    "deviceId": "360TY420703025288",
    "deviceName": "小白",
    "deviceType": "WoSweeperMini",
    "enableCloudService": True,
    "hubDeviceId": ""
}
_state_wo_sweeper_mini = {
    "deviceId": "360TY420703025288",
    "deviceType": "WoSweeperMini",
    "workingStatus": "ChargeDone",
    "onlineStatus": "online",
    "battery": 100
}

_dev_hub2 = {
    "deviceId": "E6F6EC55B0D0",
    "deviceName": "Hub 2 D0",
    "deviceType": "Hub 2",
    "enableCloudService": True,
    "hubDeviceId": ""
}

_state_hub2 = {
    "deviceId": "E6F6EC55B0D0",
    "deviceType": "Hub 2",
    "hubDeviceId": "E6F6EC55B0D0",
    "humidity": 56,
    "temperature": 21,
    "lightLevel": 7,
    "version": "V1.5-1.0"
}


def test_switchbot_device_schema():
    for data in [_dev_plug_mini_CFD2, _dev_motion_sensor_CDA5, _dev_wo_sweeper_mini, _dev_hub2]:
        obj = model.SwitchBotDevice.load(data)
        assert isinstance(obj, model.SwitchBotDevice)
        assert obj.device_id == data.get('deviceId')
        assert obj.device_name == data.get('deviceName')
        assert obj.device_type == data.get('deviceType')
        assert obj.enable_cloud_service == data.get('enableCloudService')
        assert obj.hub_device_id == data.get('hubDeviceId')
        assert obj.dump() == data


def test_switchbot_status_schema():
    for data in [_state_plug_mini_CFD2, _state_plug_mini_FF22, _state_wo_sweeper_mini, _state_hub2]:
        obj = model.SwitchBotStatus.load(data)
        assert isinstance(obj, model.SwitchBotStatus)
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
    obj = model.SwitchBotScene.load(data)
    assert isinstance(obj, model.SwitchBotScene)
    assert obj.scene_id == data.get('sceneId')
    assert obj.scene_name == data.get('sceneName')
    assert obj.dump() == data


def test_switchbot_user_repo_schema():
    data = {
        'userId': 'user_id',
        'userSecret': 'secret',
        'userToken': 'token',
        'devices': [_dev_plug_mini_CFD2, _dev_plug_mini_FF22],
        'states': [_state_plug_mini_CFD2, _state_plug_mini_FF22],
        'changes': [_change_plug_mini_FF22],
        'scenes': [],
        'subscribers': [],
        'webhooks': []
    }
    obj = model.SwitchBotUserRepo.load(data)
    logger.info(f'{type(obj)}')
    assert isinstance(obj, model.SwitchBotUserRepo)
    assert obj.uid == 'user_id'
    assert len(obj.devices) == 2
    assert obj.dump() == data


def test_switchbot_webhook_report_change():
    data = {
        "eventType": "changeReport",
        "eventVersion": "1",
        "context": {
            "deviceType": "WoPlugUS",
            "deviceMac": "6055F930FF22",
            "powerState": "ON",
            "timeOfSample": 1698720698088
        }
    }
    obj = model.SwitchBotChangeReport.load(data)
    logger.info(f'{type(obj)}')
    assert isinstance(obj, model.SwitchBotChangeReport)
    assert obj.event_type == data.get("eventType")
    assert obj.event_version == data.get("eventVersion")
    assert obj.context == data.get("context")
    assert obj.dump() == data


def test_switchbot_command_schema():
    testdatas = [{
        "commandType": "command",
        "command": "createKey",
        "parameter": {
            "name": "Guest Code",
            "type": "timeLimit",
            "password": "12345678",
            "startTime": 1664640056,
            "endTime": 1665331432
        }
    },
        {
            "command": "turnOn",
            "parameter": "default",
            "commandType": "command"
        },
        {
            "command": "setColor",
            "parameter": "122:80:20",
            "commandType": "command"
        }
    ]
    for data in testdatas:
        obj = model.SwitchBotCommand.load(data)
        assert isinstance(obj, model.SwitchBotCommand)
        assert obj.command == data.get("command")
        assert obj.commandType == data.get("commandType")
        assert obj.parameter == data.get("parameter")
        assert obj.dump() == data
