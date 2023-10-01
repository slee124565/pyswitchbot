import os
import sys
import abc
import json
import logging
from typing import Set, List
from switchbot.domain.model import SwitchBotDevice
from switchbot.adapters.json_schema import SwitchBotDeviceSchema

logger = logging.getLogger(__name__)


class AbstractRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  # type: Set[SwitchBotDevice]

    def add(self, devices: List[SwitchBotDevice]):
        self._add(devices)

    def get(self, dev_id: str) -> SwitchBotDevice:
        dev = self._get(dev_id)
        if dev:
            self.seen.add(dev)
        return dev

    def list(self, user_id: str) -> List[SwitchBotDevice]:
        dev_list = self._list(user_id)
        self.seen.update(dev_list)
        return dev_list

    @abc.abstractmethod
    def _add(self, devices: List[SwitchBotDevice]):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, dev_id: str) -> SwitchBotDevice:
        raise NotImplementedError

    @abc.abstractmethod
    def _list(self, user_id: str) -> List[SwitchBotDevice]:
        raise NotImplementedError


class FileRepository(AbstractRepository):
    _file: str = '.repository'
    _devices = []  # type:List['SwitchBotDevice']

    def _load(self):
        if not os.path.exists(self._file):
            # logger.warning(f'repository file {self._file} not exist')
            self._devices = []
            return

        with open(self._file) as file:
            _schema = SwitchBotDeviceSchema()
            self._devices = [_schema.load(d) for d in json.loads(file.read()).get('devices', [])]

    def _save(self):
        with open(self._file, 'w', encoding='utf-8') as file:
            _schema = SwitchBotDeviceSchema()
            file.write(
                json.dumps({
                    'devices': [_schema.dump(d) for d in self._devices]},
                    ensure_ascii=False, indent=2)
            )

    def _add(self, devices: List[SwitchBotDevice]):
        for dev in devices:
            if dev.device_id not in [d.device_id for d in self._devices]:
                self._devices.append(dev)
        self._save()

    def _get(self, dev_id: str) -> SwitchBotDevice:
        for dev in self._devices:
            if dev.device_id == dev_id:
                return dev
        raise ValueError(f'device ({dev_id}) not found')

    def _list(self, user_id: str) -> List[SwitchBotDevice]:
        return self._devices


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        super().__init__()
        self.session = session

    # def _add(self, product):
    #     self.session.add(product)
    #
    # def _get(self, sku):
    #     return self.session.query(model.Product).filter_by(sku=sku).first()
    #
    # def _get_by_batchref(self, batchref):
    #     return (
    #         self.session.query(model.Product)
    #         .join(model.Batch)
    #         .filter(
    #             orm.batches.c.reference == batchref,
    #         )
    #         .first()
    #     )
