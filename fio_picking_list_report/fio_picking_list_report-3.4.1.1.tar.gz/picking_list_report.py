# -*- coding: utf-8 -*-
"""
    picking_list_report.py

"""

from trytond.pool import PoolMeta, Pool
from trytond.transaction import Transaction

from openlabs_report_webkit import ReportWebkit


__metaclass__ = PoolMeta
__all__ = ['PickingListReport']


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
        options = {
            'margin-bottom': '0.50in',
            'margin-left': '0.50in',
            'margin-right': '0.50in',
            'margin-top': '0.50in',
            'footer-font-size': '8',
            'footer-left': company,
            'footer-line': '',
            'footer-right': '[page]/[toPage]',
            'footer-spacing': '5',
            'page-size': 'Letter',
        }
        return super(ReportMixin, cls).wkhtml_to_pdf(
            data, options=options
        )


class PickingListReport(ReportMixin):
    """
    HTML Report for Picking List
    """
    __name__ = 'stock.shipment.out.picking_list.html'

    @classmethod
    def parse(cls, report, records, data, localcontext):
        compare_context = cls.get_compare_context(report, records, data)

        sorted_moves = {}
        for shipment in records:
            sorted_moves[shipment.id] = sorted(
                shipment.inventory_moves,
                lambda x, y: cmp(
                    cls.get_compare_key(x, compare_context),
                    cls.get_compare_key(y, compare_context)
                )
            )

        localcontext['moves'] = sorted_moves

        return super(PickingListReport, cls).parse(
            report, records, data, localcontext
        )

    @staticmethod
    def get_compare_context(report, records, data):
        Location = Pool().get('stock.location')

        from_location_ids = set()
        to_location_ids = set()
        for record in records:
            for move in record.inventory_moves:
                from_location_ids.add(move.from_location)
                to_location_ids.add(move.to_location)

        from_locations = Location.browse(list(from_location_ids))
        to_locations = Location.browse(list(to_location_ids))

        return {
            'from_location_ids': [l.id for l in from_locations],
            'to_location_ids': [l.id for l in to_locations],
        }

    @staticmethod
    def get_compare_key(move, compare_context):
        from_location_ids = compare_context['from_location_ids']
        to_location_ids = compare_context['to_location_ids']
        return [from_location_ids.index(move.from_location.id),
                to_location_ids.index(move.to_location.id)]
