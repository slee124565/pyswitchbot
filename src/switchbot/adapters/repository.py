import uuid
import os
import abc
import json
import logging
from typing import Set, List
from switchbot.domain import model
from switchbot.adapters import orm_json

logger = logging.getLogger(__name__)


class AbstractRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  # type: Set[model.SwitchBotUserRepo]

    def register(self, user: model.SwitchBotUserRepo):
        self._register(user=user)
        self.seen.add(user)

    @abc.abstractmethod
    def get_dev_state_by_did(self, uid: str, did: str) -> model.SwitchBotStatus:
        raise NotImplementedError

    @abc.abstractmethod
    def get_by_secret(self, secret: str) -> model.SwitchBotUserRepo:
        raise NotImplementedError

    @abc.abstractmethod
    def get_by_uid(self, uid: str) -> model.SwitchBotUserRepo:
        raise NotImplementedError

    def unregister(self, uid: str = None):
        """todo: 新增 user.account_status, 參考 slack 用戶帳號狀態 Active|Inactive|Deactivated
        todo: send UserAccountDeactivated event for publish
        """
        self._unregister(uid=uid)

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
    def _register(self, user: model.SwitchBotUserRepo):
        raise NotImplementedError

    @abc.abstractmethod
    def _unregister(self, uid: str):
        raise NotImplementedError

    # @abc.abstractmethod
    # def _get_dev_by_id(self, dev_id: str) -> model.SwitchBotDevice:
    #     raise NotImplementedError
    #
    # @abc.abstractmethod
    # def _get(self, user_id: str) -> model.SwitchBotUserRepo:
    #     raise NotImplementedError
    #
    # @abc.abstractmethod
    # def _add(self, user_id: str, devices: List[model.SwitchBotDevice]):
    #     raise NotImplementedError
    #
    # @abc.abstractmethod
    # def _remove(self, user_id: str):
    #     raise NotImplementedError


class MemoryRepository(AbstractRepository):
    def get_by_secret(self, secret: str) -> model.SwitchBotUserRepo:
        return next((u for u in self._users if u.secret == secret), None)

    def get_by_uid(self, uid: str) -> model.SwitchBotUserRepo:
        return next((u for u in self._users if u.uid == uid), None)

    def _unregister(self, uid: str):
        n = next((n for n, u in enumerate(self._users) if u.uid == uid))
        if n is not None:
            del self._users[n]

    def _register(self, user: model.SwitchBotUserRepo):
        u = self.get_by_uid(uid=user.uid)
        if u:  # uid already exist, replace
            n = next((n for n, u in self._users if u.uid == user.uid))
            del self._users[n]
        self._users.append(user)

    def __init__(self):
        super().__init__()
        self._users = []  # type:List[model.SwitchBotUserRepo]

    # def _remove(self, user_id: str):
    #     n = next((n for n, user in enumerate(self._users) if user.uid == user_id), None)
    #     if n is not None:
    #         del self._users[n]
    #     else:
    #         raise ValueError(f'User ({user_id}) not exist')
    #
    # def _get_dev_by_id(self, dev_id: str) -> model.SwitchBotDevice:
    #     for user in self._users:
    #         return next((dev for dev in user.devices if dev.device_id == dev_id))
    #     raise ValueError(f'Device ({dev_id}) not exist')
    #
    # def _get(self, user_id: str) -> model.SwitchBotUserRepo:
    #     return next((user for user in self._users if user.uid == user_id), None)
    #
    # def _add(self, user_id: str, devices: List[model.SwitchBotDevice]):
    #     user = self._get(user_id=user_id)
    #     user.devices.extend(devices)


class JsonFileRepository(AbstractRepository):
    # _users = []  # type:List['SwitchBotUserRepo']

    def __init__(self, session):
        super().__init__()
        self.session = session  # type:'orm_json.MarshmallowSchemaConverter'

    def get_by_secret(self, secret: str) -> model.SwitchBotUserRepo:
        return self.session.get_by_secret(secret=secret)

    def get_by_uid(self, uid: str) -> model.SwitchBotUserRepo:
        return self.session.get_by_uid(uid=uid)

    def _register(self, user: model.SwitchBotUserRepo):
        # todo: encrypted save (secret, token) with user_id
        self.session.register_user(user)

    def _unregister(self, uid: str):
        self.session.unregister_user(uid=uid)

    # def _load(self):
    #     if not os.path.exists(self._file):
    #         self._users = []
    #     else:
    #         with open(self._file) as file:
    #             _dataset = json.loads(file.read())
    #             if not isinstance(_dataset, list):
    #                 raise ValueError(f'File ({self._file}) format invalid')
    #             for data in _dataset:
    #                 self._users.append(model.SwitchBotUserRepo.load(data))
    #
    # def _save(self):
    #     with open(self._file, 'w', encoding='utf-8') as file:
    #         _dataset = [user.dump() for user in self._users]
    #         file.write(json.dumps(_dataset, ensure_ascii=False, indent=2))
    #
    # def _get(self, user_id: str) -> model.SwitchBotUserRepo:
    #     return next((user for user in self._users if user.uid == user_id), None)
    #
    # def _get_dev_by_id(self, dev_id: str) -> model.SwitchBotDevice:
    #     _all_devices = []
    #     for user in self._users:
    #         _all_devices.extend(user.devices)
    #     return next((dev for dev in _all_devices if dev.device_id == dev_id), None)
    #
    # def _add(self, user_id: str, devices: List[model.SwitchBotDevice]):
    #     user = self._get(user_id=user_id)
    #     if user is None:
    #         raise ValueError(f'User ({user_id}) not exist')
    #
    #     for _dev in devices:
    #         _check = next((n for n, dev in list(enumerate(user.devices)) if dev.device_id == _dev.device_id), None)
    #         if _check is not None:
    #             logger.warning(f'Add duplicated device ({_dev.device_id}) for user ({user_id})')
    #             del user.devices[_check]
    #         else:
    #             user.devices.append(_dev)
    #     self._save()
    #
    # def _remove(self, user_id: str):
    #     _check = next((n for n, user in enumerate(self._users) if user.uid == user_id), None)
    #     if _check is None:
    #         raise ValueError(f'User ({user_id}) not exist')
    #     else:
    #         del self._users[_check]
    #     self._save()

# class SqlAlchemyRepository(AbstractRepository):
#     def __init__(self, session):
#         super().__init__()
#         self.session = session
