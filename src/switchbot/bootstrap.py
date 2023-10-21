""""""
import inspect
from switchbot.service_layer import handlers, messagebus, unit_of_work
from switchbot.adapters import orm, iot_api_server


def bootstrap(
        uow: unit_of_work.AbstractUnitOfWork = unit_of_work.MemoryUnitOfWork(),
        start_orm: bool = False,
        iot: iot_api_server.AbstractIotApiServer = iot_api_server.SwitchBotApiServer()
) -> messagebus.MessageBus:
    """todo: Register >> inject iot_api_server"""

    if start_orm:
        orm.start_mappers()

    dependencies = {'uow': uow}
    injected_event_handlers = {
        event_type: [
            inject_dependencies(handler, dependencies)
            for handler in event_handlers
        ]
        for event_type, event_handlers in handlers.EVENT_HANDLERS.items()
    }
    injected_command_handlers = {
        command_type: inject_dependencies(handler, dependencies)
        for command_type, handler in handlers.COMMAND_HANDLERS.items()
    }

    return messagebus.MessageBus(
        uow=uow,
        event_handlers=injected_event_handlers,
        command_handlers=injected_command_handlers,
    )


def inject_dependencies(handler, dependencies):
    params = inspect.signature(handler).parameters
    deps = {
        name: dependency
        for name, dependency in dependencies.items()
        if name in params
    }
    return lambda message: handler(message, **deps)
