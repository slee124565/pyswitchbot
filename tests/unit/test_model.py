from switchbot.domain.model import SwitchBotUser
from switchbot.domain.model import SwitchBotDevice


def test_new_device_added_for_user():
    """
    原本用戶設備為0，經過查詢得到用戶設備為2，經過sync之後，用戶設備為2
    """
    devices = [
        SwitchBotDevice(device_id='6055F92FCFD2',
                        device_name='小風扇開關',
                        device_type='Plug Mini (US)',
                        enable_cloud_service=True,
                        hub_device_id=''),
        SwitchBotDevice(device_id='6055F930FF22',
                        device_name='風扇開關',
                        device_type='Plug Mini (US)',
                        enable_cloud_service=True,
                        hub_device_id=''),
    ]
    user = SwitchBotUser(secret='secret', token='token', devices=[])
    user.sync(devices=devices)
    assert len(user.devices) == 2
    assert set([dev.device_id for dev in user.devices]) == {'6055F92FCFD2', '6055F930FF22'}


def test_device_updated_for_user():
    """設備名稱變更"""
    sync_devices = [SwitchBotDevice(device_id='6055F92FCFD2',
                                    device_name='小風扇開關',
                                    device_type='Plug Mini (US)',
                                    enable_cloud_service=True,
                                    hub_device_id=''),
                    SwitchBotDevice(device_id='6055F930FF22',
                                    device_name='床頭燈',
                                    device_type='Plug Mini (US)',
                                    enable_cloud_service=True,
                                    hub_device_id='')]
    user = SwitchBotUser(
        secret='secret', token='token',
        devices=[SwitchBotDevice(device_id='6055F92FCFD2',
                                 device_name='小風扇開關',
                                 device_type='Plug Mini (US)',
                                 enable_cloud_service=True,
                                 hub_device_id=''),
                 SwitchBotDevice(device_id='6055F930FF22',
                                 device_name='風扇開關',
                                 device_type='Plug Mini (US)',
                                 enable_cloud_service=True,
                                 hub_device_id='')]
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


def test_device_removed_for_user():
    sync_devices = [SwitchBotDevice(device_id='6055F92FCFD2',
                                    device_name='小風扇開關',
                                    device_type='Plug Mini (US)',
                                    enable_cloud_service=True,
                                    hub_device_id='')]
    user = SwitchBotUser(
        secret='secret', token='token',
        devices=[SwitchBotDevice(device_id='6055F92FCFD2',
                                 device_name='小風扇開關',
                                 device_type='Plug Mini (US)',
                                 enable_cloud_service=True,
                                 hub_device_id=''),
                 SwitchBotDevice(device_id='6055F930FF22',
                                 device_name='風扇開關',
                                 device_type='Plug Mini (US)',
                                 enable_cloud_service=True,
                                 hub_device_id='')]
    )
    user.sync(devices=sync_devices)
    assert len(user.devices) == 1
    device = user.devices[0]
    assert device.device_id == '6055F92FCFD2'
    assert device.device_name == '小風扇開關'
    assert device.device_type == 'Plug Mini (US)'


def test_device_no_changed_for_user():
    sync_devices = [SwitchBotDevice(device_id='6055F92FCFD2',
                                    device_name='小風扇開關',
                                    device_type='Plug Mini (US)',
                                    enable_cloud_service=True,
                                    hub_device_id=''),
                    SwitchBotDevice(device_id='6055F930FF22',
                                    device_name='床頭燈',
                                    device_type='Plug Mini (US)',
                                    enable_cloud_service=True,
                                    hub_device_id='')]
    user = SwitchBotUser(secret='secret', token='token', devices=sync_devices)
    user.sync(devices=sync_devices)
    assert len(user.devices) == 2
    assert set([dev.device_id for dev in user.devices]) == {'6055F92FCFD2', '6055F930FF22'}
