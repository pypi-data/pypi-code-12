# -*- coding: utf-8 -*-
from trytond.pool import Pool
from stock import ShipmentOut, Move
from report_html_stock import PickingList, SupplierRestockingList, \
    CustomerReturnRestockingList, ConsolidatedPickingList, DeliveryNote, \
    ProductLedger, ProductLedgerStartView, ProductLedgerReport, \
    InternalShipmentReport


def register():
    Pool.register(
        ShipmentOut,
        Move,
        ProductLedgerStartView,
        module='report_html_stock', type_='model'
    )
    Pool.register(
        ProductLedger,
        module='report_html_stock', type_='wizard'
    )
    Pool.register(
        PickingList,
        SupplierRestockingList,
        CustomerReturnRestockingList,
        ConsolidatedPickingList,
        DeliveryNote,
        ProductLedgerReport,
        InternalShipmentReport,
        module='report_html_stock', type_='report'
    )
