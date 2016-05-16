# -*- coding: utf-8 -*-
"""
    :copyright: (c) 2015 by Fulfil.IO Inc.
    :license: BSD, see LICENSE for more details.
"""
from trytond.model import fields
from trytond.pool import PoolMeta, Pool

__metaclass__ = PoolMeta
__all__ = ['ShipmentOut', 'Move']


class ShipmentOut:
    __name__ = 'stock.shipment.out'

    sales = fields.Function(
        fields.One2Many('sale.sale', None, 'Sales'),
        getter='get_sales', searcher='search_sales'
    )

    def get_sales(self, name=None):
        """
        Returns sales associated with a shipment.
        """
        sales = set([m.sale.id for m in self.moves if m.sale])
        return list(sales)

    @classmethod
    def search_sales(cls, name, clause):
        return [('moves.sale',) + tuple(clause[1:])]

    def _get_inventory_move(self, move):
        """
        Write origin also to inventory moves
        """
        new_move = super(ShipmentOut, self)._get_inventory_move(move)

        # Added a field inventory_origin for the reports to keep track of
        # corresponding outgoing move's origin
        # This is particularly used in picking list report where we need
        # to print inventory moves and we need corresponding outgoing
        # moves origin
        new_move.inventory_origin = move.origin
        return new_move


class Move:
    __name__ = 'stock.move'

    inventory_origin = fields.Reference(
        'Inventory Origin', selection='get_origin', readonly=True
    )
    sale_order = fields.Function(
        fields.Many2One('sale.sale', 'Sale'), 'get_sale_order'
    )

    def get_sale_order(self, name):
        """
        Get sale order from move origin
        """
        SaleLine = Pool().get('sale.line')
        ShipmentOut = Pool().get('stock.shipment.out')

        if not self.shipment:
            return None

        origin = self.origin or self.inventory_origin

        if isinstance(self.shipment, ShipmentOut) and \
                isinstance(origin, SaleLine):
            return origin.sale.id
