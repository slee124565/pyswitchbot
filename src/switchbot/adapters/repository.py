import os
import abc
import json
import logging
from typing import Set, List
from dataclasses import asdict
from switchbot.domain import model
from .file_repository import UserRepo, UserRepoSchema

logger = logging.getLogger(__name__)


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


class FileRepository(AbstractRepository):
    _file: str
    _repo: UserRepo

    def _load(self):
        if not os.path.exists(self._file):
            logger.warning(f'repository file {self._file} not exist')
            return

        with open(self._file) as file:
            data = json.loads(file.read())
        user_repo_schema = UserRepoSchema()
        self._repo = user_repo_schema.load(data)
        logger.debug(f'_repo {self._repo}')

    def _save(self):
        with open(self._file, 'w', encoding='utf-8') as file:
            json.dump(asdict(self._repo), file, ensure_ascii=False, indent=2)

    def __init__(self, repo_file: str = '.repository'):
        super().__init__()
        self._file = repo_file
        self._load()

    def _add(self, devices: List[model.SwitchBotDevice]):
        raise NotImplementedError

    def _get(self, dev_id: str) -> model.SwitchBotDevice:
        raise NotImplementedError

    def _list(self, user_id: str) -> List[model.SwitchBotDevice]:
        raise NotImplementedError
