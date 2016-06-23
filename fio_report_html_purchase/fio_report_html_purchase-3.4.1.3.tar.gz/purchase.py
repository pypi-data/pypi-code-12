# -*- coding: utf-8 -*-
from trytond.pool import Pool
from trytond.model import fields, ModelView
from trytond.transaction import Transaction
from trytond.wizard import Wizard, StateAction, StateView, Button

from openlabs_report_webkit import ReportWebkit

__all__ = [
    'PurchaseReport', 'PurchaseReportWizardStart', 'PurchaseReportWizard',
    'PurchaseOrder'
]


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


class PurchaseOrder(ReportMixin):
    __name__ = 'purchase.purchase.html'


class PurchaseReport(ReportMixin):
    "Purchase Report"
    __name__ = 'report.purchase'

    @classmethod
    def parse(cls, report, records, data, localcontext):
        Purchase = Pool().get('purchase.purchase')
        Party = Pool().get('party.party')
        Product = Pool().get('product.product')

        domain = [
            ('state', 'in', ['confirmed', 'processing', 'done']),
            ('purchase_date', '>=', data['start_date']),
            ('purchase_date', '<=', data['end_date'])
        ]

        supplier_id = data.get('supplier')
        product_id = data.get('product')

        if supplier_id:
            domain.append(('party', '=', supplier_id))
        if product_id:
            domain.append(('lines.product', '=', product_id))

        purchases = Purchase.search(domain)

        localcontext.update({
            'purchases': purchases,
            'supplier': supplier_id and Party(supplier_id),
            'product': product_id and Product(product_id),
        })
        return super(PurchaseReport, cls).parse(
            report, records, data, localcontext
        )


class PurchaseReportWizardStart(ModelView):
    """
    Purchase Report Wizard View
    """
    __name__ = 'report.purchase.wizard.start'

    supplier = fields.Many2One('party.party', 'Supplier')
    product = fields.Many2One('product.product', 'Product')
    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)

    @staticmethod
    def default_start_date():
        Date = Pool().get('ir.date')

        return Date.today()

    @staticmethod
    def default_end_date():
        Date = Pool().get('ir.date')

        return Date.today()


class PurchaseReportWizard(Wizard):
    """
    Wizard to generage Purchases report
    """
    __name__ = 'report.purchase.wizard'

    start = StateView(
        'report.purchase.wizard.start',
        'report_html_purchase.report_purchase_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Generate', 'generate', 'tryton-ok', default=True),
        ]
    )
    generate = StateAction('report_html_purchase.report_purchase')

    def do_generate(self, action):
        """
        Sends the wizard data to report
        """
        data = {
            'supplier': self.start.supplier and self.start.supplier.id,
            'product': self.start.product and self.start.product.id,
            'start_date': self.start.start_date,
            'end_date': self.start.end_date,
        }
        return action, data

    def transition_generate(self):
        return 'end'
