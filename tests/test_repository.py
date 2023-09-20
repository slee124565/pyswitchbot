from dataclasses import dataclass
from typing import List, Dict
from marshmallow import Schema, fields, post_load


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
    devices: List[Device]
    scenes: List[Scene]
    webhooks: List[str]


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


json_data = {
    'users': {
        'user1': {
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

# Deserialize JSON to Python Object
users_schema = UserRepoSchema()
users_object = users_schema.load(json_data)

# Serialize Python Object to JSON
users_json = users_schema.dump(users_object)

print(users_object)
print(users_json)
