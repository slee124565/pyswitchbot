import logging
from switchbot.service_layer import unit_of_work
from switchbot.domain import model
from switchbot import gh_intent

logger = logging.getLogger(__name__)


def user_profile_by_uid(uid: str, uow: unit_of_work.AbstractUnitOfWork) -> dict:
    with uow:
        u = uow.users.get_by_uid(uid=uid)
        data = {}
        if u:
            data.update({
                'uid': u.uid,
                'devices': len(u.devices),
                'states': len(u.states),
                'changes': len(u.changes),
            })
        return data


def user_profile_by_secret(secret: str, uow: unit_of_work.AbstractUnitOfWork) -> dict:
    with uow:
        u = uow.users.get_by_secret(secret=secret)
        data = {}
        if u:
            data.update({
                'uid': u.uid,
                'devices': len(u.devices),
                'states': len(u.states),
                'changes': len(u.changes),
            })
        return data


def _convert_dev_to_aog_sync_dto(dev: model.SwitchBotDevice) -> gh_intent.SyncDevice:
    if dev.device_type in ['Plug Mini (US)']:
        _dev_id = dev.device_id
        _dev_type = "action.devices.types.OUTLET"
        _dev_traits = ["action.devices.traits.OnOff"]
        _name = dev.device_name
        _will_report_state = True
        sync_dev = gh_intent.SyncDevice(
            device_id=_dev_id,
            name=gh_intent.SyncDeviceName(name=_name),
            device_type=_dev_type,
            traits=_dev_traits,
            will_report_state=_will_report_state
        )
    else:
        logger.warning(f'device object: {dev.dump()}')
        raise NotImplementedError

    return sync_dev


def get_user_sync_intent_fulfillment(
        uid: str, subscriber_id: str, request_id: str, uow: unit_of_work.AbstractUnitOfWork
):
    """
    0. 檢查 subscriber_id 是否屬於 user.subscribers
    1. 設定 agentUserId = uid
    2. 設定 user device sync data list
    """
    with uow:
        u = uow.users.get_by_uid(uid=uid)
        if subscriber_id not in u.subscribers:
            raise ValueError(f'{subscriber_id} not in user {uid} subscribers')

        sync_dto = gh_intent.SyncResponse(
            requestId=request_id,
            payload=gh_intent.SyncResponsePayload(
                agentUserId=f"{u.uid}",
                devices=[_convert_dev_to_aog_sync_dto(dev) for dev in u.devices]
            )
        )
    return sync_dto.dump()


def convert_dev_to_aog_query_dto(user: model.SwitchBotUserRepo, dev: model.SwitchBotDevice) -> dict:
    if dev.device_type in ['Plug Mini (US)']:
        state = user.get_dev_state(dev_id=dev.device_id)
        return {
            "on": True if state.power == "on" else False,
            "online": True,
            "status": "SUCCESS"
        }
    else:
        logger.warning(f'device object: {dev.dump()}')
        raise NotImplementedError


def get_user_query_intent_fulfillment(
        uid: str, subscriber_id: str, devices_dto: dict, uow: unit_of_work.AbstractUnitOfWork
) -> dict:
    """
    1. 檢查 subscriber_id 是否屬於 user.subscribers
    2.
    """
    with uow:
        u = uow.users.get_by_uid(uid=uid)
        if subscriber_id not in u.subscribers:
            raise ValueError(f'{subscriber_id} not in user {uid} subscribers')
        fulfillment = {
            "devices": {
                f"{dev.device_id}": convert_dev_to_aog_query_dto(user=u, dev=dev)
                for dev in u.devices if dev.device_id in [d.get("id") for d in devices_dto]
            }
        }
    return fulfillment


def get_user_exec_intent_fulfillment(
        uid: str, subscriber_id: str, aog_cmds_dto: list, uow: unit_of_work.AbstractUnitOfWork
):
    """todo"""
    with uow:
        u = uow.users.get_by_uid(uid=uid)
        if subscriber_id not in u.subscribers:
            raise ValueError(f'{subscriber_id} not in user {uid} subscribers')
        for cmd_dto in aog_cmds_dto:
            dev_ids = [d.get("id") for d in cmd_dto.get("devices")]
            # execution = cmd_dto.get("execution")[0]
            # _aog_dto =
            raise NotImplementedError
        fulfillment = {
            "commands": [
            ]
        }
    return fulfillment
