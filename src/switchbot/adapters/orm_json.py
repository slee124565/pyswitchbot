import os
import logging
import json
from typing import List
from switchbot.domain import model
from switchbot.domain.model import SwitchBotUserRepoSchema

logger = logging.getLogger(__name__)


class OrmJsonSchemaError(Exception):
    pass


class MarshmallowSchemaDatastore:
    _users = []  # type: List['model.SwitchBotUserRepo']

    def __init__(self, file: str):
        self._file = file
        if os.path.exists(file):
            with open(self._file, 'r') as fh:
                content = json.loads(fh.read())
                if not isinstance(content, list):
                    raise OrmJsonSchemaError
            _schema = SwitchBotUserRepoSchema()
            self._users = [_schema.load(data) for data in content]
        else:
            self._users = []

    def commit(self):
        self._save()

    def _save(self):
        with open(self._file, 'w') as fh:
            _schema = SwitchBotUserRepoSchema()
            content = [_schema.dump(u) for u in self._users]
            fh.write(json.dumps(content, indent=2, ensure_ascii=False))

    def register_user(self, user: model.SwitchBotUserRepo):
        n, u = next(((n, u) for n, u in enumerate(self._users) if u.secret == user.secret), (None, None))
        if u is None:
            self._users.append(user)
        else:
            logger.warning(f'register w/ secret already exist on user {u.uid}, skip')
            # del self._users[n]
            # self._users.append(user)
        self._save()

    def unregister_user(self, user: model.SwitchBotUserRepo):
        uid = user.uid
        n, u = next(((n, u) for n, u in enumerate(self._users) if u.uid == uid), (None, None))
        if u is None:
            m = f'user uid {uid} not exist'
            logger.warning(m)
            raise ValueError(m)
        else:
            del self._users[n]
            logger.info(f'unregister user {u}, replaced with new user {u}')
        self._save()

    def get_by_secret(self, secret: str) -> model.SwitchBotUserRepo:
        return next((u for u in self._users if u.secret == secret), None)

    def get_by_uid(self, uid: str) -> model.SwitchBotUserRepo:
        return next((u for u in self._users if u.uid == uid), None)

    def get_by_dev_id(self, dev_id) -> model.SwitchBotUserRepo:
        return next((u for u in self._users for d in u.devices if d.device_id == dev_id), None)

    def get_dev_state(self, uid: str, dev_id: str) -> model.SwitchBotStatus:
        u = self.get_by_uid(uid=uid)
        return next((s for s in u.states if s.device_id == dev_id), None)

    def get_dev_last_change_report(self, uid: str, dev_id: str) -> model.SwitchBotChangeReport:
        u = self.get_by_uid(uid=uid)
        return next((c for c in u.changes[::-1] if c.context.get("deviceMac") == dev_id), None)

    def count(self) -> int:
        return len(self._users)


def session_factory(file: str):
    return MarshmallowSchemaDatastore(file)
