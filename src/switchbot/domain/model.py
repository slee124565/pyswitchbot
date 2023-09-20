import json
from typing import Optional
from dataclasses import dataclass, field
from . import commands, events


class SwitchBotDevice:
    deviceId: str
    deviceName: str
    deviceType: str
    enableCloudService: bool
    hubDeviceId: str

    def __init__(self, **kwargs):
        self.deviceId = kwargs.get('deviceId')
        self.deviceName = kwargs.get('deviceName')
        self.deviceType = kwargs.get('deviceType')
        self.enableCloudService = kwargs.get('enableCloudService')
        self.hubDeviceId = kwargs.get('hubDeviceId')

    def __repr__(self):
        return f'Device({self.deviceId}, {self.deviceName}, {self.deviceType})'


class SwitchBotDeviceStatus:
    kwargs: dict

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __repr__(self):
        return f'DevStatus({json.dumps(self.kwargs)})'


@dataclass
class SwitchBotScene:
    sceneId: str
    sceneName: str


@dataclass
class SwitchBotWebhook:
    url: str
    createTime: int | None
    lastUpdateTime: int | None
    deviceList: str | None
    enable: bool | None
