from dataclasses import dataclass


class Command:
    pass


class SwitchBotDevCmd(Command):
    dev_id: str
    pass


@dataclass
class CheckAuthToken(Command):
    secret: str
    token: str


@dataclass
class GetDeviceList(Command):
    secret: str
    token: str
