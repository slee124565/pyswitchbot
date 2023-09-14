from typing import Union
from dataclasses import dataclass


class Command:
    pass


@dataclass
class ExecManualScene(Command):
    secret: str
    token: str
    scene_id: str


@dataclass
class SendDeviceCtrlCmd(Command):
    secret: str
    token: str
    dev_id: str
    cmd_type: str
    cmd_value: str
    cmd_param: Union[str, dict]


@dataclass
class SwitchBotDevCommand(Command):
    commandType: str
    command: str
    parameter: Union[str, dict]


@dataclass
class CheckAuthToken(Command):
    secret: str
    token: str


@dataclass
class GetDeviceList(Command):
    secret: str
    token: str
