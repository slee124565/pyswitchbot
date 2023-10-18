import os
import abc
import json
import logging
from typing import Set, List
from switchbot.domain.model import SwitchBotUserRepo, SwitchBotDevice, SwitchBotStatus

logger = logging.getLogger(__name__)


class AbstractRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  # type: Set[SwitchBotDevice]

    # def sync(self, user_id: str) -> List[SwitchBotDevice]:
    #     user = self._get_user(user_id=user_id)
    #     if user:
    #         return user.devices
    #     else:
    #         raise ValueError(f'User({user_id}) not exist')
    #
    # def query(self, dev_id_list: List[str]) -> List[SwitchBotStatus]:
    #     devices = [self._get_dev_by_id(dev_id=dev_id) for dev_id in dev_id_list]
    #     states = [dev.state for dev in devices]
    #     return states

    # def execute(self, dev_id: str, cmd: SwitchBotCmd):
    #     raise NotImplementedError

    def remove(self, user_id: str):
        self._remove(user_id=user_id)

    def update_dev_state(self, state: SwitchBotStatus):
        dev = self._get_dev_by_id(dev_id=state.device_id)
        dev.state = state

    def get_user(self, user_id: str) -> SwitchBotUserRepo:
        """todo: rename to get"""
        return self._get_user(user_id)

    # def get(self, user_id: str) -> List[SwitchBotDevice]:
    #     devices = self._get(user_id)
    #     if devices:
    #         for dev in devices:
    #             self.seen.add(dev)
    #     return devices

    def add(self, user_id: str, devices: List[SwitchBotDevice]):
        self._add(user_id=user_id, devices=devices)

    # def list(self, user_id: str) -> List[SwitchBotDevice]:
    #     dev_list = self._list(user_id)
    #     self.seen.update(dev_list)
    #     return dev_list

    # def update(self, status: SwitchBotStatus):
    #     self._update(status)

    @abc.abstractmethod
    def _get_dev_by_id(self, dev_id: str) -> SwitchBotDevice:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_user(self, user_id: str) -> SwitchBotUserRepo:
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, user_id: str) -> SwitchBotUserRepo:
        raise NotImplementedError

    @abc.abstractmethod
    def _add(self, user_id: str, devices: List[SwitchBotDevice]):
        raise NotImplementedError

    @abc.abstractmethod
    def _remove(self, user_id: str):
        raise NotImplementedError

# @abc.abstractmethod
# def _list(self, user_id: str) -> List[SwitchBotDevice]:
#     raise NotImplementedError
#
# @abc.abstractmethod
# def _update(self, status: SwitchBotStatus):
#     raise NotImplementedError


class FileRepository(AbstractRepository):
    _file: str = '.repository'
    _devices = []  # type:List['SwitchBotDevice']
    _states = []  # type:List['SwitchBotStatus']

    def __init__(self, file: str = '.repository'):
        super().__init__()
        self._file = file
        self._load()

    def _load(self):
        if not os.path.exists(self._file):
            # logger.warning(f'repository file {self._file} not exist')
            self._devices = []
            self._states = []
            return

        with open(self._file) as file:
            _data = json.loads(file.read())
            self._devices = [SwitchBotDevice.load(d) for d in _data.get('devices', [])]
            self._states = [SwitchBotStatus.load(s) for s in _data.get('states', [])]

    def _save(self):
        with open(self._file, 'w', encoding='utf-8') as file:
            _data = {
                'devices': [SwitchBotDevice.dump(d) for d in self._devices],
                'states': [SwitchBotStatus.dump(s) for s in self._states]
            }
            file.write(json.dumps(_data, ensure_ascii=False, indent=2))

    def _get_dev_by_id(self, dev_id: str) -> SwitchBotDevice:
        return next((dev for dev in self._devices if dev.device_id == dev_id))

    def _get_user(self, user_id: str) -> SwitchBotUserRepo:
        return SwitchBotUserRepo(user_id=user_id, devices=self._devices, scenes=[], webhooks=[])

    def _add(self, user_id: str, devices: List[SwitchBotDevice]):
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

    def _update(self, status: SwitchBotStatus):
        """
        loop all states
        if dev_id not exist, append
        else remove old and add new
        """
        # self._states.append(status)
        for i, s in enumerate(self._states):
            if status.device_id == s.device_id:
                # 若存在，更新該設備資訊
                self._states[i] = status
                self._save()
                return

            # 若不存在該設備，則添加到列表中
        self._states.append(status)
        self._save()


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
