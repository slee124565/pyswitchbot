from switchbot.domain.model import SwitchBotUser
from switchbot.domain.model import SwitchBotDevice


def test_user_sync_with_new_device_added():
    """設備新增"""
    devices = [
        SwitchBotDevice(
            device_id='6055F92FCFD2',
            device_name='小風扇開關',
            device_type='Plug Mini (US)',
            enable_cloud_service=True,
            hub_device_id=''
        ),
        SwitchBotDevice(
            device_id='6055F930FF22',
            device_name='風扇開關',
            device_type='Plug Mini (US)',
            enable_cloud_service=True,
            hub_device_id=''
        ),
    ]
    user = SwitchBotUser(secret='secret', token='token', devices=[])

    user.sync(devices=devices)

    assert len(user.devices) == 2
    assert set([dev.device_id for dev in user.devices]) == {'6055F92FCFD2', '6055F930FF22'}


def test_user_sync_with_device_name_changed():
    """設備名稱變更"""
    sync_devices = [
        SwitchBotDevice(
            device_id='6055F92FCFD2',
            device_name='小風扇開關',
            device_type='Plug Mini (US)',
            enable_cloud_service=True,
            hub_device_id=''
        ),
        SwitchBotDevice(
            device_id='6055F930FF22',
            device_name='床頭燈',
            device_type='Plug Mini (US)',
            enable_cloud_service=True,
            hub_device_id=''
        )
    ]
    user = SwitchBotUser(
        secret='secret', token='token',
        devices=[
            SwitchBotDevice(
                device_id='6055F92FCFD2',
                device_name='小風扇開關',
                device_type='Plug Mini (US)',
                enable_cloud_service=True,
                hub_device_id=''
            ),
            SwitchBotDevice(
                device_id='6055F930FF22',
                device_name='風扇開關',
                device_type='Plug Mini (US)',
                enable_cloud_service=True,
                hub_device_id=''
            )
        ]
    )

    user.sync(devices=sync_devices)

    for dev in user.devices:
        if dev.device_id == '6055F92FCFD2':
            assert dev.device_name == '小風扇開關'
        elif dev.device_id == '6055F930FF22':
            assert dev.device_name == '床頭燈'
        else:
            assert False
    assert len(user.devices) == 2


def test_user_sync_with_device_removed():
    """設備移除"""
    sync_devices = [
        SwitchBotDevice(
            device_id='6055F92FCFD2',
            device_name='小風扇開關',
            device_type='Plug Mini (US)',
            enable_cloud_service=True,
            hub_device_id=''
        )
    ]
    user = SwitchBotUser(
        secret='secret', token='token',
        devices=[
            SwitchBotDevice(
                device_id='6055F92FCFD2',
                device_name='小風扇開關',
                device_type='Plug Mini (US)',
                enable_cloud_service=True,
                hub_device_id=''
            ),
            SwitchBotDevice(
                device_id='6055F930FF22',
                device_name='風扇開關',
                device_type='Plug Mini (US)',
                enable_cloud_service=True,
                hub_device_id=''
            )
        ]
    )

    user.sync(devices=sync_devices)

    assert len(user.devices) == 1
    device = user.devices[0]
    assert device.device_id == '6055F92FCFD2'
    assert device.device_name == '小風扇開關'
    assert device.device_type == 'Plug Mini (US)'


def test_user_sync_device_with_no_changed():
    """設備維持不變"""
    sync_devices = [
        SwitchBotDevice(
            device_id='6055F92FCFD2',
            device_name='小風扇開關',
            device_type='Plug Mini (US)',
            enable_cloud_service=True,
            hub_device_id=''
        ),
        SwitchBotDevice(
            device_id='6055F930FF22',
            device_name='床頭燈',
            device_type='Plug Mini (US)',
            enable_cloud_service=True,
            hub_device_id=''
        )
    ]
    user = SwitchBotUser(secret='secret', token='token', devices=sync_devices)

    user.sync(devices=sync_devices)

    assert len(user.devices) == 2
    assert set([dev.device_id for dev in user.devices]) == {'6055F92FCFD2', '6055F930FF22'}


def test_user_disconnect_from_service():
    """用戶終止設備連線整合控制"""
    sync_devices = [
        SwitchBotDevice(
            device_id='6055F92FCFD2',
            device_name='小風扇開關',
            device_type='Plug Mini (US)',
            enable_cloud_service=True,
            hub_device_id=''
        ),
        SwitchBotDevice(
            device_id='6055F930FF22',
            device_name='床頭燈',
            device_type='Plug Mini (US)',
            enable_cloud_service=True,
            hub_device_id=''
        )
    ]
    user = SwitchBotUser(secret='secret', token='token', devices=sync_devices)

    user.disconnect()

    assert len(user.devices) == 0


def test_device_query_on_one_device():
    """查詢用戶設備狀態"""
    raise NotImplementedError


def test_device_query_on_multi_device():
    raise NotImplementedError


def test_device_exec_one_cmd_on_one_device():
    raise NotImplementedError


def test_device_exec_one_cmd_on_multi_device():
    raise NotImplementedError


def test_device_exec_diff_cmd_on_diff_device():
    raise NotImplementedError
