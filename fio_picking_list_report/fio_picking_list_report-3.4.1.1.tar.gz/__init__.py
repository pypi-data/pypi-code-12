# -*- coding: utf-8 -*-
"""
    __init__.py

"""
from trytond.pool import Pool
from picking_list_report import PickingListReport


def register():
    Pool.register(
        PickingListReport,
        module='picking_list_report', type_='report'
    )
