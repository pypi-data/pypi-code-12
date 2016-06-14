# coding: utf-8
from m3_ext.ui.app_ui import (
    DesktopShortcut, DesktopLoader)
from m3_users import metaroles, GENERIC_USER
from demo.app.helpers import find_pack
from demo.app import controller
from demo.app.reports.actions import (
    ReportListActionPack)

__author__ = 'damirazo <me@damirazo.ru>'


def register_actions():
    controller.action_controller.extend_packs([
        ReportListActionPack(),
    ])


def register_desktop_menu():
    generic_metarole = metaroles.get_metarole(GENERIC_USER)

    reports_root = DesktopShortcut(
        name=ReportListActionPack.title,
        pack=find_pack(ReportListActionPack),
        index=20
    )

    DesktopLoader.add(
        metarole=generic_metarole,
        place=DesktopLoader.TOPTOOLBAR,
        element=reports_root,
    )
