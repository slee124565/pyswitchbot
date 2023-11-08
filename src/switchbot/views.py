from switchbot.service_layer import unit_of_work


def user_profile(secret: str, uow: unit_of_work.JsonFileUnitOfWork) -> dict:
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
