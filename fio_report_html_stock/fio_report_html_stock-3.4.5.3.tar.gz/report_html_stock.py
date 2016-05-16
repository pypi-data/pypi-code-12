# -*- coding: utf-8 -*-
from itertools import groupby, imap, chain
from dateutil.relativedelta import relativedelta

from trytond.pool import Pool, PoolMeta
from trytond.model import fields, ModelView
from trytond.wizard import Wizard, Button, StateAction, StateView
from trytond.transaction import Transaction

from openlabs_report_webkit import ReportWebkit

__all__ = [
    'PickingList', 'SupplierRestockingList', 'CustomerReturnRestockingList',
    'ConsolidatedPickingList', 'ProductLedgerStartView', 'ProductLedgerReport',
    'ProductLedger', 'InternalShipmentReport'
]
__metaclass__ = PoolMeta


class ReportMixin(ReportWebkit):
    """
    Mixin Class to inherit from, for all HTML reports.
    """

    @classmethod
    def wkhtml_to_pdf(cls, data, options=None):
        """
        Call wkhtmltopdf to convert the html to pdf
        """
        Company = Pool().get('company.company')

        company = ''
        if Transaction().context.get('company'):
            company = Company(Transaction().context.get('company')).party.name
        opts = {
            'margin-bottom': '0.50in',
            'margin-left': '0.50in',
            'margin-right': '0.50in',
            'margin-top': '0.50in',
            'footer-font-size': '8',
            'footer-left': company,
            'footer-line': '',
            'footer-right': '[page]/[toPage]',
            'footer-spacing': '5',
            "page-size": "Letter"
        }
        if options:
            opts.update(options)
        return super(ReportMixin, cls).wkhtml_to_pdf(
            data, options=opts
        )

    @classmethod
    def get_sorted_moves(cls, records):
        """
        Sorting the moves for each shipment
        """
        sorted_moves = {}
        for shipment in records:
            sorted_moves[shipment.id] = sorted(
                shipment.inventory_moves,
                key=lambda m: (m.from_location, m.to_location)
            )
        return sorted_moves


class PickingList(ReportMixin):
    """
    Picking List Report
    """
    __name__ = 'report.picking_list'

    @staticmethod
    def sort_inventory_moves(shipment, sort_key=None):
        """
        A sorter that can be overwritten by downstream modules
        """
        return sorted(shipment.inventory_moves, key=sort_key)

    @classmethod
    def parse(cls, report, records, data, localcontext):
        localcontext['sort_inventory_moves'] = cls.sort_inventory_moves
        localcontext['sort_key'] = lambda move: (
            move.from_location.rec_name, move.product.name
        )
        return super(PickingList, cls).parse(
            report, records, data, localcontext
        )


class ConsolidatedPickingList(ReportMixin):
    """
    Consolidated Picking List.
    """
    __name__ = 'report.consolidated_picking_list'

    @classmethod
    def group_key(cls, move):
        """
        Key function for grouping and sorting of
        moves
        """
        return (move.from_location, move.product)

    @classmethod
    def get_moves(cls, shipment):
        return shipment.inventory_moves

    @classmethod
    def get_product_repr_from(cls, key):
        """
        Returns the product representation from the key
        """
        return key[1].rec_name

    @classmethod
    def get_location_repr_from(cls, key):
        """
        Returns the location representation from the key
        """
        return key[0].rec_name

    @classmethod
    def parse(cls, report, records, data, localcontext):
        """
        The default implementation groups by product
        and sorts by from_location.
        """
        localcontext['grouped_moves'] = []
        for key, grouper in groupby(
                # Sort all the moves from all shipments
                # and then group it
                list(sorted(
                    # Chain all inventory moves from all shipments
                    chain(*imap(lambda s: cls.get_moves(s), records)),
                    key=cls.group_key
                )), cls.group_key):
            moves = list(grouper)
            # TODO: Sum totals everything, the UOM to base UOM conversion
            # is not done
            localcontext['grouped_moves'].append(
                (key, moves, sum(map(lambda m: m.quantity, moves)))
            )

        localcontext['get_product_repr_from'] = cls.get_product_repr_from
        localcontext['get_location_repr_from'] = cls.get_location_repr_from
        return super(ConsolidatedPickingList, cls).parse(
            report, records, data, localcontext
        )


class SupplierRestockingList(ReportMixin):
    'Supplier Restocking List'
    __name__ = 'report.supplier_restocking_list'

    @classmethod
    def parse(cls, report, records, data, localcontext):

        sorted_moves = cls.get_sorted_moves(records)

        localcontext['moves'] = sorted_moves

        return super(SupplierRestockingList, cls).parse(
            report, records, data, localcontext
        )


class CustomerReturnRestockingList(ReportMixin):
    'Customer Return Restocking List'
    __name__ = 'report.customer_return_restocking_list'

    @classmethod
    def parse(cls, report, records, data, localcontext):

        sorted_moves = cls.get_sorted_moves(records)

        localcontext['moves'] = sorted_moves

        return super(CustomerReturnRestockingList, cls).parse(
            report, records, data, localcontext
        )


class DeliveryNote(ReportMixin):
    "Delivery Note"
    __name__ = 'report.delivery_note'


class InternalShipmentReport(ReportMixin):
    __name__ = 'report.internal_shipment'


class ProductLedgerStartView(ModelView):
    'Product Ledger Start'
    __name__ = 'product.product.ledger.start'

    products = fields.One2Many(
        'product.product', None, 'Products', required=True,
        domain=[
            ('type', '=', 'goods')
        ], add_remove=[('type', '=', 'goods')]
    )
    warehouses = fields.One2Many(
        'stock.location', None, 'Warehouses',
        domain=[
            ('type', '=', 'warehouse')
        ], add_remove=[('type', '=', 'warehouse')]
    )
    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)

    @staticmethod
    def default_start_date():
        Date = Pool().get('ir.date')
        return Date.today() - relativedelta(months=1)

    @staticmethod
    def default_end_date():
        Date = Pool().get('ir.date')
        return Date.today()


class ProductLedgerReport(ReportMixin):
    'Product Ledger Report'
    __name__ = 'report.product_ledger'

    @classmethod
    def get_purchases(cls, product_id, data):
        Move = Pool().get('stock.move')

        return Move.search([
            ('effective_date', '>=', data['start_date']),
            ('effective_date', '<=', data['end_date']),
            ('product', '=', product_id),
            ('state', '=', 'done'),
            ('from_location.type', '=', 'supplier'),
        ], order=[('effective_date', 'asc')])

    @classmethod
    def get_productions(cls, product_id, data):
        Move = Pool().get('stock.move')

        return Move.search([
            ('effective_date', '>=', data['start_date']),
            ('effective_date', '<=', data['end_date']),
            ('product', '=', product_id),
            ('state', '=', 'done'),
            ('from_location.type', '=', 'production'),
        ], order=[('effective_date', 'asc')])

    @classmethod
    def get_customers(cls, product_id, data):
        Move = Pool().get('stock.move')

        return Move.search([
            ('effective_date', '>=', data['start_date']),
            ('effective_date', '<=', data['end_date']),
            ('product', '=', product_id),
            ('state', '=', 'done'),
            ('to_location.type', '=', 'customer'),
        ], order=[('effective_date', 'asc')])

    @classmethod
    def get_lost_and_founds(cls, product_id, data):
        Move = Pool().get('stock.move')

        return Move.search([
            ('effective_date', '>=', data['start_date']),
            ('effective_date', '<=', data['end_date']),
            ('product', '=', product_id),
            ('state', '=', 'done'),
            ('from_location.type', '=', 'lost_found'),
        ], order=[('effective_date', 'asc')])

    @classmethod
    def get_consumed(cls, product_id, data):
        Move = Pool().get('stock.move')

        return Move.search([
            ('effective_date', '>=', data['start_date']),
            ('effective_date', '<=', data['end_date']),
            ('product', '=', product_id),
            ('state', '=', 'done'),
            ('to_location.type', '=', 'production'),
        ], order=[('effective_date', 'asc')])

    @classmethod
    def _get_total_quantity(cls, moves):
        """
        Returns sum of quantity for list of stock moves
        """
        sum = 0.0
        for move in moves:
            sum += move.internal_quantity
        return sum

    @classmethod
    def get_summary(cls, record, data):
        Product = Pool().get('product.product')

        rv = {}
        product = record['product']
        with Transaction().set_context(
            locations=data['warehouses'],
            stock_date_end=data['start_date'] - relativedelta(days=1)
        ):
            rv['opening_stock'] = Product(product.id).quantity

        with Transaction().set_context(
            locations=data['warehouses'], stock_date_end=data['end_date']
        ):
            rv['closing_stock'] = Product(product.id).quantity

        rv['purchased'] = cls._get_total_quantity(record['purchases'])
        rv['produced'] = cls._get_total_quantity(record['productions'])
        rv['customer'] = cls._get_total_quantity(record['customers'])
        rv['lost'] = cls._get_total_quantity(record['lost_and_founds'])
        rv['consumed'] = cls._get_total_quantity(record['consumed'])
        return rv

    @classmethod
    def parse(cls, report, objects, data, localcontext):
        Product = Pool().get('product.product')
        Locations = Pool().get('stock.location')

        records = []
        summary = {}
        for product_id in data['products']:
            product = Product(product_id)
            record = {
                'product': product,
                'purchases': cls.get_purchases(product.id, data),
                'productions': cls.get_productions(product.id, data),
                'customers': cls.get_customers(product.id, data),
                'lost_and_founds': cls.get_lost_and_founds(product.id, data),
                'consumed': cls.get_consumed(product.id, data)
            }
            records.append(record)
            summary[product] = cls.get_summary(record, data)

        localcontext['summary'] = summary
        localcontext['warehouses'] = Locations.browse(data['warehouses'])
        return super(ProductLedgerReport, cls).parse(
            report, records, data, localcontext
        )


class ProductLedger(Wizard):
    'Wizard for generating product ledger'
    __name__ = 'product.product.ledger.wizard'

    start = StateView(
        'product.product.ledger.start',
        'report_html_stock.wizard_product_ledger_start_form',
        [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('View', 'view', 'tryton-go-next', default=True),
        ]
    )
    view = StateAction('report_html_stock.report_product_ledger')

    def default_start(self, fields):
        return {
            'products': Transaction().context.get('active_ids'),
        }

    def do_view(self, action):
        data = {
            'products': map(int, self.start.products),
            'warehouses': map(int, self.start.warehouses),
            'start_date': self.start.start_date,
            'end_date': self.start.end_date,
        }
        return action, data
