import os
import abc
import json
import logging
from typing import Set, List
from switchbot.domain import model

logger = logging.getLogger(__name__)


class AbstractRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  # type: Set[model.SwitchBotUserRepo]

    def unregister(self, secret: str, token: str, user_id: str = None):
        """todo"""
        raise NotImplementedError

    def register(self, secret: str, token: str, user_id: str = None):
        if not user_id:
            user_id = secret
        self._register(secret=secret, token=token, user_id=user_id)
        self.seen.add(self.get(user_id=user_id))

    def subscribe(self, secret: str):
        """todo"""
        raise NotImplementedError

    # def request_sync(self, user_id: str, devices: List[model.SwitchBotDevice]):
    #     user = self._get(user_id=user_id)
    #     if user is None:
    #         raise ValueError(f'User ({user_id}) not exist')
    #     user.request_sync(devices=devices)

    def remove(self, user_id: str):
        user = self.get(user_id=user_id)
        if user is None:
            raise ValueError(f'User ({user_id}) not exist')
        self._remove(user_id=user_id)
        self.seen.add(user)

    def update_dev_state(self, state: model.SwitchBotStatus):
        dev = self._get_dev_by_id(dev_id=state.device_id)
        dev.state = state

    def get(self, user_id: str) -> model.SwitchBotUserRepo:
        return self._get(user_id)

    def add(self, user_id: str, devices: List[model.SwitchBotDevice]):
        self._add(user_id=user_id, devices=devices)

    @abc.abstractmethod
    def _register(self, secret: str, token: str, user_id: str):
        raise NotImplementedError

    @abc.abstractmethod
    def _get_dev_by_id(self, dev_id: str) -> model.SwitchBotDevice:
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, user_id: str) -> model.SwitchBotUserRepo:
        raise NotImplementedError

    @abc.abstractmethod
    def _add(self, user_id: str, devices: List[model.SwitchBotDevice]):
        raise NotImplementedError

    @abc.abstractmethod
    def _remove(self, user_id: str):
        raise NotImplementedError


class MemoryRepository(AbstractRepository):
    def _register(self, secret: str, token: str, user_id: str):
        self._users.append(
            model.SwitchBotUserRepo(
                user_id=user_id,
                secret=secret,
                token=token,
                devices=[],
                states=[],
                scenes=[],
                webhooks=[]
            )
        )

    def _remove(self, user_id: str):
        n = next((n for n, user in enumerate(self._users) if user.user_id == user_id), None)
        if n is not None:
            del self._users[n]
        else:
            raise ValueError(f'User ({user_id}) not exist')

    def _get_dev_by_id(self, dev_id: str) -> model.SwitchBotDevice:
        for user in self._users:
            return next((dev for dev in user.devices if dev.device_id == dev_id))
        raise ValueError(f'Device ({dev_id}) not exist')

    def __init__(self):
        super().__init__()
        self._users = []  # type:List['SwitchBotUserRepo']

    def _get(self, user_id: str) -> model.SwitchBotUserRepo:
        return next((user for user in self._users if user.user_id == user_id), None)

    def _add(self, user_id: str, devices: List[model.SwitchBotDevice]):
        user = self._get(user_id=user_id)
        user.devices.extend(devices)


class FileRepository(AbstractRepository):
    _file: str
    _users = []  # type:List['SwitchBotUserRepo']

    # _devices = []  # type:List['SwitchBotDevice']
    # _states = []  # type:List['SwitchBotStatus']

    def __init__(self, file):
        super().__init__()
        self._file = file
        self._load()

    def _register(self, secret: str, token: str, user_id: str):
        # todo: encrypted save (secret, token) with user_id
        self._users.append(
            model.SwitchBotUserRepo(
                user_id=user_id,
                secret=secret,
                token=token,
                devices=[],
                states=[],
                scenes=[],
                webhooks=[]
            )
        )
        self._save()

    def _load(self):
        if not os.path.exists(self._file):
            self._users = []
        else:
            with open(self._file) as file:
                _dataset = json.loads(file.read())
                if not isinstance(_dataset, list):
                    raise ValueError(f'File ({self._file}) format invalid')
                for data in _dataset:
                    self._users.append(model.SwitchBotUserRepo.load(data))

    def _save(self):
        with open(self._file, 'w', encoding='utf-8') as file:
            _dataset = [user.dump() for user in self._users]
            file.write(json.dumps(_dataset, ensure_ascii=False, indent=2))

    def _get(self, user_id: str) -> model.SwitchBotUserRepo:
        return next((user for user in self._users if user.user_id == user_id), None)

    def _get_dev_by_id(self, dev_id: str) -> model.SwitchBotDevice:
        _all_devices = []
        for user in self._users:
            _all_devices.extend(user.devices)
        return next((dev for dev in _all_devices if dev.device_id == dev_id), None)

    def _add(self, user_id: str, devices: List[model.SwitchBotDevice]):
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
        self._save()

    def _remove(self, user_id: str):
        _check = next((n for n, user in enumerate(self._users) if user.user_id == user_id), None)
        if _check is None:
            raise ValueError(f'User ({user_id}) not exist')
        else:
            del self._users[_check]
        self._save()

# class SqlAlchemyRepository(AbstractRepository):
#     def __init__(self, session):
#         super().__init__()
#         self.session = session
