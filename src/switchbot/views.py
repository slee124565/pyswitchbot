# from typing import Union
from dataclasses import asdict
from switchbot.service_layer import unit_of_work


def read_webhook_config(secret: str, token: str, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        _config = uow.devices.read_webhook_config(
            secret=secret,
            token=token
        )
    return _config


def get_scene_list(secret: str, token: str, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        scene_list = uow.devices.get_scene_list(
            secret=secret,
            token=token
        )
    return [asdict(scene) for scene in scene_list]


def get_device_list(secret: str, token: str, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        dev_list = uow.devices.get_dev_list(
            secret=secret,
            token=token
        )
    return [asdict(dev) for dev in dev_list]


def get_device_status(secret: str, token: str, dev_id, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        dev_status = uow.devices.get_dev_status(
            secret=secret,
            token=token,
            dev_id=dev_id
        )
    return dev_status.kwargs
# def send_device_ctrl_cmd(secret: str, token: str, dev_id: str, cmd_type: str, cmd_value: str,
#                          cmd_param: Union[str, dict], uow: unit_of_work.AbstractUnitOfWork):
#     with uow:
#         response = uow.devices.send_dev_ctrl_cmd(
#             secret=secret,
#             token=token,
#             dev_id=dev_id,
#             cmd_type=cmd_type,
#             cmd_value=cmd_value,
#             cmd_param=cmd_param
#         )
#     return response
