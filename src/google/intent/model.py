from typing import List, Optional, Dict
from marshmallow import Schema, INCLUDE, fields, post_load, post_dump


class ExecutionItemSchema(Schema):
    command = fields.Str(required=True)
    params = fields.Dict()

    @post_load
    def make_execution_item(self, data, **kwargs):
        return ExecutionItem(**data)

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items()
            if value is not None
        }


class DeviceItemSchema(Schema):
    id = fields.Str(required=True)
    customData = fields.Dict()

    @post_load
    def make_device_item(self, data, **kwargs):
        return DeviceItem(**data)

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items()
            if value is not None
        }


class CommandItemSchema(Schema):
    devices = fields.List(fields.Nested(DeviceItemSchema()), required=True)
    execution = fields.List(fields.Nested(ExecutionItemSchema()), required=True)

    @post_load
    def make_command_item(self, data, **kwargs):
        return CommandItem(**data)


class _PayloadSchema(Schema):
    commands = fields.List(fields.Nested(CommandItemSchema()), required=True)

    @post_load
    def make_payload(self, data, **kwargs):
        return _Payload(**data)


class InputItemSchema(Schema):
    intent = fields.Str(required=True)
    payload = fields.Nested(_PayloadSchema(), required=True)

    @post_load
    def make_input_item(self, data, **kwargs):
        return InputItem(**data)


class ExecuteRequestSchema(Schema):
    requestId = fields.Str(required=True)
    inputs = fields.List(fields.Nested(InputItemSchema()), required=True)

    @post_load
    def make_execute_request(self, data, **kwargs):
        return ExecuteRequest(**data)


class ExecutionItem:
    def __init__(self, command, params=None):
        self.command = command  # type:str
        self.params = params if params else {}  # type:dict


class DeviceItem:
    def __init__(self, id, customData=None):
        self.id = id  # type:str
        self.customData = customData if customData else {}  # type:dict


class CommandItem:
    def __init__(self, devices, execution):
        self.devices = devices  # type:List[DeviceItem]
        self.execution = execution  # type:List[ExecutionItem]


class _Payload:
    def __init__(self, commands):
        self.commands = commands  # type:List[CommandItem]


class InputItem:
    def __init__(self, intent, payload):
        self.intent = intent  # type:str
        self.payload = payload  # Payload is an object of Payload class


class ExecuteRequest:
    def __init__(self, requestId, inputs):
        self.requestId = requestId  # type:str
        self.inputs = inputs  # type:List[InputItem]

    @classmethod
    def load(cls, data: dict):
        return ExecuteRequestSchema().load(data)

    def dump(self) -> dict:
        return ExecuteRequestSchema().dump(self)


# 以下為 Response 部分
class CommandResponseItemSchema(Schema):
    ids = fields.List(fields.Str(), required=True)
    status = fields.Str(required=True)
    states = fields.Dict()
    errorCode = fields.Str()

    @post_load
    def make_command_response_item(self, data, **kwargs):
        return CommandResponseItem(**data)

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items()
            if value is not None
        }


class ResponsePayloadSchema(Schema):
    errorCode = fields.Str()
    debugString = fields.Str()
    commands = fields.List(fields.Nested(CommandResponseItemSchema()))

    @post_load
    def make_response_payload(self, data, **kwargs):
        return ResponsePayload(**data)

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items()
            if value is not None
        }


class ExecuteResponseSchema(Schema):
    requestId = fields.Str(required=True)
    payload = fields.Nested(ResponsePayloadSchema(), required=True)

    @post_load
    def make_execute_response(self, data, **kwargs):
        return ExecuteResponse(**data)


class CommandResponseItem:
    def __init__(self, ids, status, states=None, errorCode=None):
        self.ids = ids  # type:List[str]
        self.status = status  # type:str
        self.states = states  # type:dict
        self.errorCode = errorCode  # type:str


class ResponsePayload:
    def __init__(self, errorCode=None, debugString=None, commands=None):
        self.errorCode = errorCode  # type:str
        self.debugString = debugString  # type:str
        self.commands = commands if commands else []  # type:CommandResponseItem


class ExecuteResponse:
    def __init__(self, requestId, payload):
        self.requestId = requestId  # type:str
        self.payload = payload  # type:ResponsePayload

    @classmethod
    def load(cls, data: dict):
        return ExecuteResponseSchema().load(data)

    def dump(self) -> dict:
        return ExecuteResponseSchema().dump(self)


class QueryDeviceItemSchema(Schema):
    id = fields.Str(required=True)
    customData = fields.Dict()

    @post_load
    def make_query_device_item(self, data, **kwargs):
        return QueryDeviceItem(**data)

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items()
            if value is not None
        }


class QueryPayloadSchema(Schema):
    devices = fields.List(fields.Nested(QueryDeviceItemSchema()), required=True)

    @post_load
    def make_query_payload(self, data, **kwargs):
        return QueryPayload(**data)


class QueryInputItemSchema(Schema):
    intent = fields.Str(required=True)
    payload = fields.Nested(QueryPayloadSchema(), required=True)

    @post_load
    def make_query_input_item(self, data, **kwargs):
        return QueryInputItem(**data)


class QueryRequestSchema(Schema):
    requestId = fields.Str(required=True)
    inputs = fields.List(fields.Nested(QueryInputItemSchema()), required=True)

    @post_load
    def make_query_request(self, data, **kwargs):
        return QueryRequest(**data)


class QueryDeviceItem:
    def __init__(self, id: str, customData: Optional[Dict] = None):
        self.id = id
        self.customData = customData


class QueryPayload:
    def __init__(self, devices: List[QueryDeviceItem]):
        self.devices = devices


class QueryInputItem:
    def __init__(self, intent: str, payload: QueryPayload):
        self.intent = intent
        self.payload = payload


class QueryRequest:
    def __init__(self, requestId: str, inputs: List[QueryInputItem]):
        self.requestId = requestId
        self.inputs = inputs

    @classmethod
    def load(cls, data: dict):
        return QueryRequestSchema().load(data)

    def dump(self) -> dict:
        return QueryRequestSchema().dump(self)


class QueryDeviceStatusSchema(Schema):
    online = fields.Bool(required=True)
    status = fields.Str(required=True)
    errorCode = fields.Str(required=False)
    extra_fields = fields.Dict()

    class Meta:
        unknown = INCLUDE
        # additional = fields.Dict()

    @post_load
    def make_query_device_status(self, data, **kwargs):
        defined_fields = ['online', 'status', 'errorCode']
        extra_fields = {k: v for k, v in data.items() if k not in defined_fields}
        filtered_data = {k: data[k] for k in defined_fields if k in data}
        return QueryDeviceStatus(**filtered_data, extra_fields=extra_fields)

    @post_dump
    def add_extra_fields(self, data, **kwargs):
        if 'extra_fields' in data and data['extra_fields']:
            # 合併 extra_fields 到 data
            merged = {**data, **data['extra_fields']}
            # 移除原始的 extra_fields 鍵
            merged.pop('extra_fields', None)
            return merged
        return data


class QueryResponsePayloadSchema(Schema):
    devices = fields.Dict(keys=fields.Str(), values=fields.Nested(QueryDeviceStatusSchema()), required=True)

    @post_load
    def make_query_response_payload(self, data, **kwargs):
        return QueryResponsePayload(**data)


class QueryResponseSchema(Schema):
    requestId = fields.Str(required=True)
    payload = fields.Nested(QueryResponsePayloadSchema(), required=True)

    @post_load
    def make_query_response(self, data, **kwargs):
        return QueryResponse(**data)


class QueryDeviceStatus:
    def __init__(self, online: bool, status: str, error_code: str = None, extra_fields: dict = None):
        self.online = online
        self.status = status
        self.error_code = error_code
        self.extra_fields = extra_fields if extra_fields else {}


class QueryResponsePayload:
    def __init__(self, **kwargs):
        self.devices = kwargs.get("devices")


class QueryResponse:
    def __init__(self, requestId: str, payload: QueryResponsePayload):
        self.requestId = requestId
        self.payload = payload

    @classmethod
    def load(cls, data: dict):
        return QueryResponseSchema().load(data)

    def dump(self) -> dict:
        return QueryResponseSchema().dump(self)


def _test_execute_intent():
    request = {
        "requestId": "ff36a3cc-ec34-11e6-b1a0-64510650abcf",
        "inputs": [
            {
                "intent": "action.devices.EXECUTE",
                "payload": {
                    "commands": [
                        {
                            "devices": [
                                {
                                    "id": "123",
                                    "customData": {
                                        "fooValue": 74,
                                        "barValue": True,
                                        "bazValue": "sheepdip"
                                    }
                                },
                                {
                                    "id": "456",
                                    "customData": {
                                        "fooValue": 36,
                                        "barValue": False,
                                        "bazValue": "moarsheep"
                                    }
                                }
                            ],
                            "execution": [
                                {
                                    "command": "action.devices.commands.OnOff",
                                    "params": {
                                        "on": True
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
        ]
    }
    # assert ExecuteRequestSchema().load(data)
    obj = ExecuteRequest.load(request)
    assert isinstance(obj, ExecuteRequest)
    assert obj.dump() == request

    response = {
        "requestId": "ff36a3cc-ec34-11e6-b1a0-64510650abcf",
        "payload": {
            "commands": [
                {
                    "ids": [
                        "123"
                    ],
                    "status": "SUCCESS",
                    "states": {
                        "on": True,
                        "online": True
                    }
                },
                {
                    "ids": [
                        "456"
                    ],
                    "status": "ERROR",
                    "errorCode": "deviceTurnedOff"
                }
            ]
        }
    }
    obj = ExecuteResponse.load(response)
    assert isinstance(obj, ExecuteResponse)
    assert obj.dump() == response


if __name__ == '__main__':
    request = {
        "requestId": "ff36a3cc-ec34-11e6-b1a0-64510650abcf",
        "inputs": [
            {
                "intent": "action.devices.QUERY",
                "payload": {
                    "devices": [
                        {
                            "id": "123",
                            "customData": {
                                "fooValue": 74,
                                "barValue": True,
                                "bazValue": "foo"
                            }
                        },
                        {
                            "id": "456",
                            "customData": {
                                "fooValue": 12,
                                "barValue": False,
                                "bazValue": "bar"
                            }
                        }
                    ]
                }
            }
        ]
    }
    obj = QueryRequest.load(request)
    assert isinstance(obj, QueryRequest)
    assert obj.dump() == request

    response = {
        "requestId": "ff36a3cc-ec34-11e6-b1a0-64510650abcf",
        "payload": {
            "devices": {
                "123": {
                    "on": True,
                    "online": True,
                    "status": "SUCCESS"
                },
                "456": {
                    "on": True,
                    "online": True,
                    "status": "SUCCESS",
                    "brightness": 80,
                    "color": {
                        "spectrumRgb": 16711935
                    }
                }
            }
        }
    }
    obj = QueryResponse.load(response)
    assert isinstance(obj, QueryResponse)
    assert obj.dump() == response
