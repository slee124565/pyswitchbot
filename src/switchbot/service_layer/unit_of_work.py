# pylint: disable=attribute-defined-outside-init
from __future__ import annotations
import abc
import os
import shutil
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.orm.session import Session
from switchbot.adapters import repository
from switchbot.adapters.iot_api_server import AbstractIotApiServer, SwitchBotApiServer, FakeApiServer


# from switchbot import config


class AbstractUnitOfWork(abc.ABC):
    users: repository.AbstractRepository
    api_server: AbstractIotApiServer

    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()

    def collect_new_events(self):
        for dev in self.users.seen:
            while dev.events:
                yield dev.events.pop(0)

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError


class FakeFileUnitOfWork(AbstractUnitOfWork):
    def __enter__(self):
        self.users = repository.FileRepository()
        self.api_server = FakeApiServer()
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)

    def _commit(self):
        pass

    def rollback(self):
        pass


class CliUnitOfWork(AbstractUnitOfWork):
    def __init__(self, file: str = '.repository'):
        self._file = file
        self._origin = os.path.join(file, '.swap')

    def __enter__(self):
        # todo: 如何整合 file repository
        if os.path.exists(self._file):
            shutil.copyfile(self._file, self._origin)
        self.users = repository.FileRepository(file=self._file)
        self.api_server = SwitchBotApiServer()
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)

    def _commit(self):
        os.remove(self._origin)

    def rollback(self):
        shutil.copyfile(self._origin, self._file)

# DEFAULT_SESSION_FACTORY = sessionmaker(
#     bind=create_engine(
#         config.get_postgres_uri(),
#         isolation_level="REPEATABLE READ",
#     )
# )
#
#
# class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
#     def __init__(self, session_factory=DEFAULT_SESSION_FACTORY):
#         self.session_factory = session_factory
#
#     def __enter__(self):
#         self.session = self.session_factory()  # type: Session
#         self.products = repository.SqlAlchemyRepository(self.session)
#         return super().__enter__()
#
#     def __exit__(self, *args):
#         super().__exit__(*args)
#         self.session.close()
#
#     def _commit(self):
#         self.session.commit()
#
#     def rollback(self):
#         self.session.rollback()
