""""""
from switchbot.service_layer import handlers, messagebus, unit_of_work


def bootstrap(
        uow: unit_of_work.AbstractUnitOfWork = unit_of_work.ApiUnitOfWork()
) -> messagebus.MessageBus:
    pass
