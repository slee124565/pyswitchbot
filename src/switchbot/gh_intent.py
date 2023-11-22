from typing import List, Optional, Dict, Any
from marshmallow import Schema, INCLUDE, fields, post_load, post_dump


class ExecuteCmdExecItemSchema(Schema):
    command = fields.Str(required=True)
    params = fields.Dict()

    @post_load
    def make_execution_item(self, data, **kwargs):
        return ExecuteCmdExecItem(**data)

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items()
            if value is not None
        }


class ExecuteCmdDevItemSchema(Schema):
    id = fields.Str(required=True)
    customData = fields.Dict()

    @post_load
    def make_device_item(self, data, **kwargs):
        return ExecuteCmdDevItem(**data)

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items()
            if value is not None
        }


class ExecuteCmdItemSchema(Schema):
    devices = fields.List(fields.Nested(ExecuteCmdDevItemSchema()), required=True)
    execution = fields.List(fields.Nested(ExecuteCmdExecItemSchema()), required=True)

    @post_load
    def make_command_item(self, data, **kwargs):
        return ExecuteCmdItem(**data)


class ExecutePayloadSchema(Schema):
    commands = fields.List(fields.Nested(ExecuteCmdItemSchema()), required=True)

    @post_load
    def make_payload(self, data, **kwargs):
        return ExecutePayload(**data)


class ExecuteInputItemSchema(Schema):
    intent = fields.Str(required=True)
    payload = fields.Nested(ExecutePayloadSchema(), required=True)

    @post_load
    def make_input_item(self, data, **kwargs):
        return ExecuteInputItem(**data)


class ExecuteRequestSchema(Schema):
    requestId = fields.Str(required=True)
    inputs = fields.List(fields.Nested(ExecuteInputItemSchema()), required=True)

    @post_load
    def make_execute_request(self, data, **kwargs):
        return ExecuteRequest(**data)


class ExecuteCmdExecItem:
    def __init__(self, command: str, params: Optional[Dict] = None):
        self.command = command  # type:str
        self.params = params if params else {}  # type:dict


class ExecuteCmdDevItem:
    def __init__(self, id: str, customData: Optional[Dict] = None):
        self.id = id  # type:str
        self.customData = customData if customData else {}  # type:dict


class ExecuteCmdItem:
    def __init__(self, devices: List[ExecuteCmdDevItem], execution: List[ExecuteCmdExecItem]):
        self.devices = devices  # type:List[ExecuteCmdDevItem]
        self.execution = execution  # type:List[ExecuteCmdExecItem]


class ExecutePayload:
    def __init__(self, commands: List[ExecuteCmdItem]):
        self.commands = commands  # type:List[ExecuteCmdItem]


class ExecuteInputItem:
    INTENT = "action.devices.EXECUTE"

    def __init__(self, intent: str, payload: ExecutePayload):
        self.intent = intent  # type:str
        self.payload = payload  # type: ExecutePayload


class ExecuteRequest:
    def __init__(self, requestId: str, inputs: List[ExecuteInputItem]):
        self.requestId = requestId  # type:str
        self.inputs = inputs  # type:List[ExecuteInputItem]

    @classmethod
    def load(cls, data: dict):
        return ExecuteRequestSchema().load(data)

    def dump(self) -> dict:
        return ExecuteRequestSchema().dump(self)


# 以下為 Response 部分
class ExecuteCommandResponseItemSchema(Schema):
    ids = fields.List(fields.Str(), required=True)
    status = fields.Str(required=True)
    states = fields.Dict()
    errorCode = fields.Str()

    @post_load
    def make_command_response_item(self, data, **kwargs):
        return ExecuteCommandResponseItem(**data)

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items()
            if value is not None
        }


class ExecuteResponsePayloadSchema(Schema):
    errorCode = fields.Str()
    debugString = fields.Str()
    commands = fields.List(fields.Nested(ExecuteCommandResponseItemSchema()))

    @post_load
    def make_response_payload(self, data, **kwargs):
        return ExecuteResponsePayload(**data)

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items()
            if value is not None
        }


class ExecuteResponseSchema(Schema):
    requestId = fields.Str(required=True)
    payload = fields.Nested(ExecuteResponsePayloadSchema(), required=True)

    @post_load
    def make_execute_response(self, data, **kwargs):
        return ExecuteResponse(**data)


class ExecuteCommandResponseItem:
    def __init__(self, ids: List[str], status: str, states: Optional[dict] = None, errorCode: str = None):
        self.ids = ids  # type:List[str]
        self.status = status  # type:str
        self.states = states  # type:dict
        self.errorCode = errorCode  # type:str


class ExecuteResponsePayload:
    def __init__(self, commands: List[ExecuteCommandResponseItem], errorCode: str = None, debugString: str = None):
        self.errorCode = errorCode  # type:str
        self.debugString = debugString  # type:str
        self.commands = commands if commands else []


class ExecuteResponse:
    def __init__(self, requestId: str, payload: ExecuteResponsePayload):
        self.requestId = requestId  # type:str
        self.payload = payload  # type:ExecuteResponsePayload

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
    INTENT = "action.devices.QUERY"

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
            return {
                key: value for key, value in merged.items()
                if value is not None
            }
        return {
            key: value for key, value in data.items()
            if value is not None
        }


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
    def __init__(self, devices: dict):
        self.devices = devices


class QueryResponse:
    def __init__(self, requestId: str, payload: QueryResponsePayload):
        self.requestId = requestId
        self.payload = payload

    @classmethod
    def load(cls, data: dict):
        return QueryResponseSchema().load(data)

    def dump(self) -> dict:
        return QueryResponseSchema().dump(self)


class SyncInputSchema(Schema):
    intent = fields.Str(required=True)

    @post_load
    def make_sync_intent_input(self, data, **kwargs):
        return SyncInput(**data)


class SyncRequestSchema(Schema):
    requestId = fields.Str(required=True)
    inputs = fields.List(fields.Nested(SyncInputSchema()), required=True)

    @post_load
    def make_sync_intent_request(self, data, **kwargs):
        return SyncRequest(**data)


class SyncInput:
    INTENT = "action.devices.SYNC"

    def __init__(self, intent: str):
        self.intent = intent


class SyncRequest:
    def __init__(self, requestId: str, inputs: List[SyncInput]):
        self.requestId = requestId
        self.inputs = inputs

    @classmethod
    def load(cls, data: dict):
        return SyncRequestSchema().load(data)

    def dump(self) -> dict:
        return SyncRequestSchema().dump(self)


class SyncDeviceInfoSchema(Schema):
    manufacturer = fields.Str()
    model = fields.Str()
    hwVersion = fields.Str()
    swVersion = fields.Str()

    @post_load
    def make_device_info(self, data, **kwargs):
        return SyncDeviceInfo(**data)

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items()
            if value is not None
        }


class SyncDeviceNameSchema(Schema):
    """{
                        "defaultNames": [
                            "My Outlet 1234"
                        ],
                        "name": "Night light",
                        "nicknames": [
                            "wall plug"
                        ]
                    }"""
    name = fields.Str(required=True)
    defaultNames = fields.List(fields.Str())
    nicknames = fields.List(fields.Str())

    @post_load
    def make_device_name(self, data, **kwargs):
        return SyncDeviceName(**data)

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items()
            if value is not None
        }


class SyncDeviceSchema(Schema):
    device_id = fields.Str(required=True, data_key='id')
    device_type = fields.Str(required=True, data_key='type')
    traits = fields.List(fields.Str(), required=True)
    name = fields.Nested(SyncDeviceNameSchema(), required=True)
    will_report_state = fields.Bool(required=True, data_key='willReportState')
    room_hint = fields.Str(data_key='roomHint')
    device_info = fields.Nested(SyncDeviceInfoSchema(), data_key='deviceInfo')
    attributes = fields.Dict()
    custom_data = fields.Dict(data_key='customData')
    other_device_ids = fields.List(fields.Dict(keys=fields.Str(), values=fields.Str()), data_key='otherDeviceIds')
    notification_supported_by_agent = fields.Bool(data_key='notificationSupportedByAgent')

    @post_load
    def make_sync_device(self, data, **kwargs):
        return SyncDevice(**data)

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items()
            if value is not None
        }


class SyncResponsePayloadSchema(Schema):
    agentUserId = fields.Str(required=True)
    devices = fields.List(fields.Nested(SyncDeviceSchema()), required=True)
    errorCode = fields.Str()
    debugString = fields.Str()

    @post_load
    def make_sync_response_payload(self, data, **kwargs):
        return SyncResponsePayload(**data)

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items()
            if value is not None
        }


class SyncResponseSchema(Schema):
    requestId = fields.Str(required=True)
    payload = fields.Nested(SyncResponsePayloadSchema(), required=True)

    @post_load
    def make_sync_response(self, data, **kwargs):
        return SyncResponse(**data)

    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {
            key: value for key, value in data.items()
            if value is not None
        }


class SyncDeviceInfo:
    def __init__(
            self,
            manufacturer: Optional[str] = None,
            model: Optional[str] = None,
            hwVersion: Optional[str] = None,
            swVersion: Optional[str] = None
    ):
        self.manufacturer = manufacturer
        self.model = model
        self.hwVersion = hwVersion
        self.swVersion = swVersion


class SyncDeviceName:
    def __init__(self, name: str, defaultNames: Optional[List[str]] = None, nicknames: Optional[List[str]] = None):
        self.defaultNames = defaultNames
        self.name = name
        self.nicknames = nicknames


class SyncDevice:
    def __init__(self, device_id: str, device_type: str, traits: List[str], name: SyncDeviceName,
                 will_report_state: bool,
                 room_hint: Optional[str] = None, device_info: Optional[SyncDeviceInfo] = None,
                 attributes: Optional[Dict[str, Any]] = None, custom_data: Optional[Dict[str, Any]] = None,
                 other_device_ids: Optional[List[Dict[str, str]]] = None,
                 notification_supported_by_agent: Optional[bool] = None):
        self.device_id = device_id
        self.device_type = device_type
        self.traits = traits
        self.name = name
        self.will_report_state = will_report_state
        self.room_hint = room_hint
        self.device_info = device_info
        self.attributes = attributes
        self.custom_data = custom_data
        self.other_device_ids = other_device_ids
        self.notification_supported_by_agent = notification_supported_by_agent

    @classmethod
    def load(cls, data: dict):
        return SyncResponseSchema().load(data)

    def dump(self) -> dict:
        return SyncResponseSchema().dump(self)


class SyncResponsePayload:
    def __init__(self, agentUserId: str, devices: List[SyncDevice], errorCode: Optional[str] = None,
                 debugString: Optional[str] = None):
        self.agentUserId = agentUserId
        self.devices = devices
        self.errorCode = errorCode
        self.debugString = debugString


class SyncResponse:
    def __init__(self, requestId: str, payload: SyncResponsePayload):
        self.requestId = requestId
        self.payload = payload

    @classmethod
    def load(cls, data: dict):
        return SyncResponseSchema().load(data)

    def dump(self) -> dict:
        return SyncResponseSchema().dump(self)
