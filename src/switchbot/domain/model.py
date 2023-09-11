from typing import List
from . import commands, events


class SwitchBotDevice:
    def __init__(self, **kwargs):
        self.events = []  # type: List[events.Event]


class SwitchBotDeviceStatus:

    def __init__(self, **kwargs):
        pass
