from dataclasses import asdict
from switchbot.service_layer import unit_of_work


def get_device_list(secret: str, token: str, uow: unit_of_work.AbstractUnitOfWork):
    with uow:
        dev_list = uow.devices.get_dev_list(
            secret=secret,
            token=token
        )
    return [asdict(dev) for dev in dev_list]
