# pylint: disable=attribute-defined-outside-init
from __future__ import annotations
import abc
import os
import shutil
from switchbot.adapters import repository, file_datastore
from switchbot.adapters.iot_api_server import AbstractIotApiServer, SwitchBotApiServer, FakeApiServer


class AbstractUnitOfWork(abc.ABC):
    users: repository.AbstractRepository

    def __enter__(self) -> AbstractUnitOfWork:
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()

    def collect_new_events(self):
        for u in self.users.seen:
            while u.events:
                yield u.events.pop(0)

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError


class JsonFileUnitOfWork(AbstractUnitOfWork):
    def __init__(self, json_file='.datastore'):
        super().__init__()
        self._json_file = json_file
        self._origin = f'{json_file}.swap'
        self.session_factory = file_datastore.session_factory

    def __enter__(self):
        if os.path.exists(self._json_file):
            shutil.copyfile(self._json_file, self._origin)
        self.session = self.session_factory(self._json_file)
        self.users = repository.JsonFileRepository(self.session)
        # self.api_server = FakeApiServer()
        return super().__enter__()

    def __exit__(self, *args):
        if os.path.exists(self._origin):
            os.remove(self._origin)
        super().__exit__(*args)

    def _commit(self):
        self.session.commit()

    def rollback(self):
        if os.path.exists(self._origin):
            shutil.copyfile(self._origin, self._json_file)


class MemoryUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.users = repository.MemoryRepository()
        self.committed = False

    def _commit(self):
        self.committed = True

    def rollback(self):
        pass


# class CliUnitOfWork(AbstractUnitOfWork):
#     def __init__(self, file: str):
#         self._file = file
#         self._origin = f'{self._file}.swap'
#
#     def __enter__(self):
#         # todo: 如何整合 file repository
#         if os.path.exists(self._file):
#             shutil.copyfile(self._file, self._origin)
#         self.users = repository.JsonFileRepository(file=self._file)
#         self.api_server = SwitchBotApiServer()
#         return super().__enter__()
#
#     def __exit__(self, *args):
#         super().__exit__(*args)
#
#     def _commit(self):
#         if os.path.exists(self._origin):
#             os.remove(self._origin)
#
#     def rollback(self):
#         if os.path.exists(self._origin):
#             shutil.copyfile(self._origin, self._file)

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
