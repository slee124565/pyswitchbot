from typing import Union
from dataclasses import asdict
from switchbot.service_layer import unit_of_work
from switchbot.adapters import switchbotapi


def read_webhook_config_detail(
        secret: str, token: str, url: str,
        uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        _config = uow.iot_api.read_webhook_config_list(
            secret=secret,
            token=token,
            url_list=[url]
        )
    return _config


def read_webhook_config(
        secret: str, token: str,
        uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        _config = uow.iot_api.read_webhook_config(
            secret=secret,
            token=token
        )
    return _config


def get_scene_list(
        secret: str, token: str,
        uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        scene_list = uow.iot_api.get_scene_list(
            secret=secret,
            token=token
        )
    return [asdict(scene) for scene in scene_list]


def get_device_list(
        secret: str, token: str,
        uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        dev_list = uow.iot_api.get_dev_list(
            secret=secret,
            token=token
        )
    return [asdict(dev) for dev in dev_list]


def get_device_status(
        secret: str, token: str, dev_id,
        uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        dev_status = uow.iot_api.get_dev_status(
            secret=secret,
            token=token,
            dev_id=dev_id
        )
    return dev_status.kwargs


def send_device_ctrl_cmd(
        secret: str, token: str, dev_id: str,
        cmd_type: str, cmd_value: str, cmd_param: Union[str, dict],
        uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        response = uow.iot_api.send_dev_ctrl_cmd(
            secret=secret,
            token=token,
            dev_id=dev_id,
            cmd_type=cmd_type,
            cmd_value=cmd_value,
            cmd_param=cmd_param
        )
    return response
