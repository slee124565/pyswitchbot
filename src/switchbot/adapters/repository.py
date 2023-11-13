import abc
import logging
from typing import Set, List
from switchbot.domain import model
from switchbot.adapters import file_datastore

logger = logging.getLogger(__name__)


class AbstractRepository(abc.ABC):
    """
    [seen] attribute 容器登記所有被呼叫的 User 物件，User events 就會被 bus handler 依序處理
    what to do 的邏輯要在這個 class 裡實現，how to do it 的邏輯要讓繼承的 repo instant 實作
    """

    def __init__(self):
        self.seen = set()  # type: Set[model.SwitchBotUserRepo]

    def get_by_dev_id(self, dev_id: str) -> model.SwitchBotUserRepo:
        return self._get_by_dev_id(dev_id=dev_id)

    def get_by_secret(self, secret: str) -> model.SwitchBotUserRepo:
        return self._get_by_secret(secret=secret)

    def get_by_uid(self, uid: str) -> model.SwitchBotUserRepo:
        return self._get_by_uid(uid=uid)

    def add(self, u):
        self._add(u=u)

    def delete(self, uid):
        self._delete(uid=uid)

    def count(self) -> int:
        return self._count()

    @abc.abstractmethod
    def _delete(self, uid):
        raise NotImplementedError

    @abc.abstractmethod
    def _get_by_uid(self, uid: str) -> model.SwitchBotUserRepo:
        raise NotImplementedError

    @abc.abstractmethod
    def _add(self, u: model.SwitchBotUserRepo):
        raise NotImplementedError

    @abc.abstractmethod
    def _get_by_dev_id(self, dev_id: str) -> model.SwitchBotUserRepo:
        raise NotImplementedError

    @abc.abstractmethod
    def _get_by_secret(self, secret: str) -> model.SwitchBotUserRepo:
        raise NotImplementedError

    @abc.abstractmethod
    def _count(self) -> int:
        raise NotImplementedError


class MemoryRepository(AbstractRepository):
    def _get_by_uid(self, uid: str) -> model.SwitchBotUserRepo:
        return next((u for u in self._users if u.uid == uid), None)

    def _get_by_dev_id(self, dev_id: str) -> model.SwitchBotUserRepo:
        return next((u for u in self._users for d in u.devices if d.device_id == dev_id), None)

    def _get_by_secret(self, secret: str) -> model.SwitchBotUserRepo:
        return next((u for u in self._users if u.secret == secret), None)

    def _delete(self, uid):
        n = next((n for n, u in enumerate(self._users) if u.uid == uid), None)
        if n is not None:
            del self._users[n]

    def _add(self, u: model.SwitchBotUserRepo):
        self._users.append(u)

    def _count(self) -> int:
        return len(self._users)

    def get_dev_last_change_report(self, uid: str, dev_id: str) -> model.SwitchBotChangeReport:
        return next((c for u in self._users if u.uid == uid
                     for c in u.changes[::-1] if c.context.get("deviceMac") == dev_id), None)

    def get_by_dev_id(self, dev_id: str) -> model.SwitchBotUserRepo:
        return next((u for u in self._users for d in u.devices if d.device_id == dev_id), None)

    def get_dev_state(self, uid: str, dev_id: str) -> model.SwitchBotStatus:
        u = self.get_by_uid(uid=uid)
        if not u:
            raise ValueError(f'uid {uid} not exist')
        return next((state for state in u.states if state.device_id == dev_id))

    def get_by_secret(self, secret: str) -> model.SwitchBotUserRepo:
        return next((u for u in self._users if u.secret == secret), None)

    def get_by_uid(self, uid: str) -> model.SwitchBotUserRepo:
        return next((u for u in self._users if u.uid == uid), None)

    def _unregister(self, user: model.SwitchBotUserRepo):
        n = next((n for n, u in enumerate(self._users) if u.uid == user.uid))
        if n is not None:
            del self._users[n]

    def _register(self, user: model.SwitchBotUserRepo):
        u = self.get_by_secret(secret=user.secret)
        if u:  # secret already exist, skip
            logger.warning(f'user {u.uid} secret already exist, skip')
            # n = next((n for n, u in enumerate(self._users) if u.secret == user.secret), None)
            # if n is not None:
            #     del self._users[n]
        else:
            self._users.append(user)
            logger.info(f'new user {user.secret} registered, fire event')

    def __init__(self):
        super().__init__()
        self._users = []  # type: List[model.SwitchBotUserRepo]


class JsonFileRepository(AbstractRepository):
    def _delete(self, uid):
        self.session.delete(uid=uid)

    def _get_by_uid(self, uid: str) -> model.SwitchBotUserRepo:
        return self.session.get_by_uid(uid=uid)

    def _add(self, u: model.SwitchBotUserRepo):
        self.session.add(user=u)

    def _get_by_dev_id(self, dev_id: str) -> model.SwitchBotUserRepo:
        return self.session.get_by_dev_id(dev_id=dev_id)

    def _get_by_secret(self, secret: str) -> model.SwitchBotUserRepo:
        return self.session.get_by_secret(secret=secret)

    def _count(self) -> int:
        return self.session.count()

    def get_by_dev_id(self, dev_id: str) -> model.SwitchBotUserRepo:
        return self.session.get_by_dev_id(dev_id=dev_id)

    # _users = []  # type:List['SwitchBotUserRepo']

    def __init__(self, session):
        super().__init__()
        self.session = session  # type:'file_datastore.FileDatastore'

# class SqlAlchemyRepository(AbstractRepository):
#     def __init__(self, session):
#         super().__init__()
#         self.session = session
