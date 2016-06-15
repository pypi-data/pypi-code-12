# coding: utf-8
from m3_ext.ui.app_ui import (
    DesktopShortcut, DesktopLoader)
from m3_users import metaroles, GENERIC_USER
from creadoc.designer.actions import CreadocDesignerActionPack
from demo.app.helpers import find_pack

__author__ = 'damirazo <me@damirazo.ru>'


def register_desktop_menu():
    generic_metarole = metaroles.get_metarole(GENERIC_USER)

    designer_root = DesktopShortcut(
        name=CreadocDesignerActionPack.title,
        pack=find_pack(CreadocDesignerActionPack),
        index=10
    )

    DesktopLoader.add(
        metarole=generic_metarole,
        place=DesktopLoader.TOPTOOLBAR,
        element=designer_root,
    )
