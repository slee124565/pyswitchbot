import logging
from switchbot.service_layer import unit_of_work
from switchbot.domain import model

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


def convert_dev_to_aog_sync_dto(dev: model.SwitchBotDevice) -> dict:
    if dev.device_type in ['Plug Mini (US)']:
        _dev_id = dev.device_id
        _dev_type = "action.devices.types.OUTLET"
        _dev_traits = ["action.devices.traits.OnOff"]
        _name = {"name": dev.device_name}
        _will_report_state = True
    else:
        logger.warning(f'device object: {dev.dump()}')
        raise NotImplementedError

    return {
        "id": _dev_id,
        "type": _dev_type,
        "traits": _dev_traits,
        "name": _name,
        "willReportState": _will_report_state,
    }


def get_user_sync_intent_fulfillment(uid: str, subscriber_id: str, uow: unit_of_work.AbstractUnitOfWork):
    """
    0. 檢查 subscriber_id 是否屬於 user.subscribers
    1. 設定 agentUserId = uid
    2. 設定 user device sync data list
    """
    with uow:
        u = uow.users.get_by_uid(uid=uid)
        if subscriber_id not in u.subscribers:
            raise ValueError(f'{subscriber_id} not in user {uid} subscribers')
        sync_payload = {
            "agentUserId": f"{uid}",
            "devices": [convert_dev_to_aog_sync_dto(dev) for dev in u.devices]
        }
    return sync_payload


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
        query_payload = {
            "devices": {
                f"{dev.device_id}": convert_dev_to_aog_query_dto(user=u, dev=dev)
                for dev in u.devices if dev.device_id in [d.get("id") for d in devices_dto]
            }
        }
    return query_payload
