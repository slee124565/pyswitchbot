"""
"""
import logging
# import json
from dataclasses import dataclass, asdict
from typing import List, Dict
from marshmallow import Schema, fields, post_load
# from .repository import AbstractRepository

logger = logging.getLogger(__name__)

TEMPLATE_DATA_MODEL = {
    'users': {
        'user1': {
            'id': 'user1',
            'devices': [
                {
                    'id': 'dev_id',
                    'name': 'dev_name',
                    'type': 'dev_type',
                    'attributes': {'key': 'value'}
                }
            ],
            'scenes': [
                {
                    'id': 'scene_id',
                    'name': 'scene_name'
                }
            ],
            'webhooks': ['url1', 'url2']
        },
        'user2': {
            'id': 'user2',
            'devices': [
                {
                    'id': 'dev_id',
                    'name': 'dev_name',
                    'type': 'dev_type',
                    'attributes': {'key': 'value'}
                }
            ],
            'scenes': [
                {
                    'id': 'scene_id',
                    'name': 'scene_name'
                }
            ],
            'webhooks': ['url1', 'url2']
        }
    }
}


@dataclass
class Device:
    id: str
    name: str
    type: str
    attributes: Dict[str, str]


@dataclass
class Scene:
    id: str
    name: str


@dataclass
class User:
    id: str
    devices: List[Device]
    scenes: List[Scene]
    webhooks: List[str]

    def __repr__(self):
        return f'User({self.id}, devices(#{len(self.devices)}), scenes(#{len(self.scenes)}), webhook(#{len(self.webhooks)})'


@dataclass
class UserRepo:
    users: Dict[str, User]


class DeviceSchema(Schema):
    id = fields.Str()
    name = fields.Str()
    type = fields.Str()
    attributes = fields.Dict()

    @post_load
    def make_device(self, data, **kwargs):
        return Device(**data)


class SceneSchema(Schema):
    id = fields.Str()
    name = fields.Str()

    @post_load
    def make_scene(self, data, **kwargs):
        return Scene(**data)


class UserSchema(Schema):
    id = fields.Str()
    devices = fields.List(fields.Nested(DeviceSchema()))
    scenes = fields.List(fields.Nested(SceneSchema()))
    webhooks = fields.List(fields.Str())

    @post_load
    def make_user(self, data, **kwargs):
        return User(**data)


class UserRepoSchema(Schema):
    users = fields.Dict(keys=fields.Str(), values=fields.Nested(UserSchema()))

    @post_load
    def make_user_repo(self, data, **kwargs):
        return UserRepo(**data)


# class FileRepository(AbstractRepository):
#     _file: str
#     _repo: UserRepo
#
#     def _load(self):
#         with open(self._file) as file:
#             data = json.loads(file.read())
#         user_repo_schema = UserRepoSchema()
#         self._repo = user_repo_schema.load(data)
#         print(self._repo)
#         pass
#
#     def _save(self):
#         with open(self._file, 'w', encoding='utf-8') as file:
#             json.dump(asdict(self._repo), file, ensure_ascii=False, indent=2)
#
#     def __init__(self, repo_file: str = '.repository'):
#         super().__init__()
#         self._file = repo_file
#         self._load()


# if __name__ == '__main__':
#     with open('.repository', 'w', encoding='utf-8') as fh:
#         fh.write(json.dumps(TEMPLATE_DATA_MODEL, ensure_ascii=False, indent=2))
#     repo = FileRepository()
