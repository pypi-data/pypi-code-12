# coding: utf-8
from m3.actions import ControllerCache


def find_pack(pack_cls):
    u"""
    Поиск инстанса пака в кэше
    :param pack_cls:
    :return:
    """
    return ControllerCache.find_pack(pack_cls)


def get_action_url(pack_cls, action_attr_name):
    pack = find_pack(pack_cls)
    action = getattr(pack, action_attr_name, None)

    url = None
    if action is not None:
        url = action.get_absolute_url()

    return url
