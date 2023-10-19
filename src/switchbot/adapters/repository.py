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

    def get(self, user_id: str) -> SwitchBotUserRepo:
        return self._get(user_id)

    def add(self, user_id: str, devices: List[SwitchBotDevice]):
        self._add(user_id=user_id, devices=devices)

    @abc.abstractmethod
    def _get_dev_by_id(self, dev_id: str) -> SwitchBotDevice:
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


class FileRepository(AbstractRepository):
    """todo: refactor to use schema json and auto save w/ .repository"""
    _file: str = '.repository'
    _users = []  # type:List['SwitchBotUserRepo']

    # _devices = []  # type:List['SwitchBotDevice']
    # _states = []  # type:List['SwitchBotStatus']

    def __init__(self, file: str = '.repository'):
        super().__init__()
        self._file = file
        self.load()

    def load(self):
        if not os.path.exists(self._file):
            self._users = []
        else:
            with open(self._file) as file:
                _dataset = json.loads(file.read())
                if not isinstance(_dataset, list):
                    raise ValueError(f'File ({self._file}) format invalid')
                for data in _dataset:
                    self._users.append(SwitchBotUserRepo.load(data))

    def save(self):
        with open(self._file, 'w', encoding='utf-8') as file:
            _dataset = [user.dump() for user in self._users]
            file.write(json.dumps(_dataset, ensure_ascii=False, indent=2))

    def _get(self, user_id: str) -> SwitchBotUserRepo:
        return next((user for user in self._users if user.user_id == user_id), None)

    def _get_dev_by_id(self, dev_id: str) -> SwitchBotDevice:
        _all_devices = []
        for user in self._users:
            _all_devices.extend(user.devices)
        return next((dev for dev in _all_devices if dev.device_id == dev_id), None)

    def _add(self, user_id: str, devices: List[SwitchBotDevice]):
        user = self._get(user_id=user_id)
        if user is None:
            raise ValueError(f'User ({user_id}) not exist')

        for _dev in devices:
            _check = next((n for n, dev in list(enumerate(user.devices)) if dev.device_id == _dev.device_id), None)
            if _check is not None:
                logger.warning(f'Add duplicated device ({_dev.device_id}) for user ({user_id})')
                del user.devices[_check]
            else:
                user.devices.append(_dev)

    def _remove(self, user_id: str):
        _check = next((n for n, user in enumerate(self._users) if user.user_id == user_id), None)
        if _check is None:
            raise ValueError(f'User ({user_id}) not exist')
        else:
            del self._users[_check]


# class SqlAlchemyRepository(AbstractRepository):
#     def __init__(self, session):
#         super().__init__()
#         self.session = session
