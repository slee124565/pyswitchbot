# pylint: disable=too-few-public-methods
from typing import List
from dataclasses import dataclass


class Event:
    pass


@dataclass
class UserRegistered(Event):
    user_id: str


@dataclass
class UserDevFetched(Event):
    user_id: str


@dataclass
class UserDevSynced(Event):
    user_id: str
