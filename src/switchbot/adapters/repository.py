import abc
from typing import Set, List
from switchbot.domain import model


class AbstractRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  # type: Set[model.SwitchBotDevice]

    def add(self, devices: List[model.SwitchBotDevice]):
        self._add(devices)

    def get(self, dev_id: str) -> model.SwitchBotDevice:
        dev = self._get(dev_id)
        if dev:
            self.seen.add(dev)
        return dev

    def list(self, user_id: str) -> List[model.SwitchBotDevice]:
        dev_list = self._list(user_id)
        self.seen.update(dev_list)
        return dev_list

    @abc.abstractmethod
    def _add(self, devices: List[model.SwitchBotDevice]):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, dev_id: str) -> model.SwitchBotDevice:
        raise NotImplementedError

    @abc.abstractmethod
    def _list(self, user_id: str) -> List[model.SwitchBotDevice]:
        raise NotImplementedError
