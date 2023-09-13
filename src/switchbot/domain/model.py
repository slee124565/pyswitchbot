import json
from typing import List
from dataclasses import dataclass
from . import commands, events


@dataclass
class SwitchBotDevice:
    deviceId: str
    deviceName: str
    deviceType: str
    enableCloudService: bool
    hubDeviceId: str

    def __repr__(self):
        return f'Device({self.deviceId}, {self.deviceName}, {self.deviceType})'


class SwitchBotDeviceStatus:
    kwargs: dict

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __repr__(self):
        return f'DevStatus({json.dumps(self.kwargs)})'
