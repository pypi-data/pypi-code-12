# -*- coding: utf-8 -*-
import sys
import os
import unittest
from dateutil.relativedelta import relativedelta

import trytond.tests.test_tryton
from trytond.tests.test_tryton import POOL, DB_NAME, USER, CONTEXT
from trytond.transaction import Transaction
from trytond.pool import Pool

from test_base import BaseTestCase

DIR = os.path.abspath(os.path.normpath(os.path.join(
    __file__, '..', '..', '..', '..', '..', 'trytond'
)))
if os.path.isdir(DIR):
    sys.path.insert(0, os.path.dirname(DIR))


class TestShipment(BaseTestCase):
    """
    Test Picking List
    """

    @unittest.skipIf(sys.platform == 'darwin', 'wkhtmltopdf repo on OSX')
    def test_0110_test_picking_list_report(self):
        """
        Test picking list report
        """
        Report = POOL.get('report.picking_list', type="report")
        Date = POOL.get('ir.date')
        ActionReport = POOL.get('ir.action.report')

        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()

            with Transaction().set_context({'company': self.company.id}):
                shipment, = self.ShipmentOut.create([{
                    'planned_date': Date.today(),
                    'effective_date': Date.today(),
                    'customer': self.party.id,
                    'warehouse': self.StockLocation.search([
                        ('type', '=', 'warehouse')
                    ])[0],
                    'delivery_address': self.party.addresses[0],
                }])
                move1, = self.Move.create([{
                    'shipment': ('stock.shipment.out', shipment.id),
                    'product': self.product.id,
                    'uom': self.uom.id,
                    'quantity': 6,
                    'from_location': shipment.warehouse.storage_location.id,
                    'to_location': shipment.warehouse.output_location.id,
                }])

                # Change the report extension to PDF
                action_report, = ActionReport.search([
                    ('name', '=', 'Picking List'),
                    ('report_name', '=', 'report.picking_list')
                ])
                action_report.extension = 'pdf'
                action_report.save()

                # Set Pool.test as False as we need the report to be generated
                # as PDF
                # This is specifically to cover the PDF coversion code
                Pool.test = False

                # Generate Picking List Report
                val = Report.execute([shipment.id], {})

                # Revert Pool.test back to True for other tests to run normally
                Pool.test = True

                self.assertTrue(val)
                # Assert report type
                self.assertEqual(val[0], 'pdf')
                # Assert report name
                self.assertEqual(val[3], 'Picking List')

    @unittest.skipIf(sys.platform == 'darwin', 'wkhtmltopdf repo on OSX')
    def test_0120_test_supplier_restocking_list_report(self):
        """
        Test Supplier Restocking list report
        """
        Report = POOL.get('report.supplier_restocking_list', type="report")
        Date = POOL.get('ir.date')
        ActionReport = POOL.get('ir.action.report')

        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()

            with Transaction().set_context({'company': self.company.id}):
                shipment, = self.ShipmentIn.create([{
                    'planned_date': Date.today(),
                    'effective_date': Date.today(),
                    'supplier': self.party.id,
                    'warehouse': self.StockLocation.search([
                        ('type', '=', 'warehouse')
                    ])[0],
                }])
                move1, = self.Move.create([{
                    'shipment': ('stock.shipment.in', shipment.id),
                    'product': self.product.id,
                    'uom': self.uom.id,
                    'quantity': 6,
                    'from_location': shipment.warehouse.input_location.id,
                    'to_location': shipment.warehouse.storage_location.id,
                }])

                # Change the report extension to PDF
                action_report, = ActionReport.search([
                    ('name', '=', 'Supplier Restocking List'),
                    ('report_name', '=', 'report.supplier_restocking_list')
                ])
                action_report.extension = 'pdf'
                action_report.save()

                # Set Pool.test as False as we need the report to be generated
                # as PDF
                # This is specifically to cover the PDF coversion code
                Pool.test = False

                # Generate Supplier Restocking List Report
                val = Report.execute([shipment.id], {})

                # Revert Pool.test back to True for other tests to run normally
                Pool.test = True

                self.assertTrue(val)
                # Assert report type
                self.assertEqual(val[0], 'pdf')
                # Assert report name
                self.assertEqual(val[3], 'Supplier Restocking List')

    @unittest.skipIf(sys.platform == 'darwin', 'wkhtmltopdf repo on OSX')
    def test_0130_test_Customer_restocking_list_report(self):
        """
        Test Supplier Restocking list report
        """
        Report = POOL.get('report.customer_return_restocking_list',
                          type="report")
        Date = POOL.get('ir.date')
        ActionReport = POOL.get('ir.action.report')

        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()

            with Transaction().set_context({'company': self.company.id}):
                shipment, = self.ShipmentOutReturn.create([{
                    'planned_date': Date.today(),
                    'effective_date': Date.today(),
                    'customer': self.party.id,
                    'warehouse': self.StockLocation.search([
                        ('type', '=', 'warehouse')
                    ])[0],
                    'delivery_address': self.party.addresses[0],
                }])
                move1, = self.Move.create([{
                    'shipment': ('stock.shipment.out.return', shipment.id),
                    'product': self.product.id,
                    'uom': self.uom.id,
                    'quantity': 6,
                    'from_location': shipment.warehouse.input_location.id,
                    'to_location': shipment.warehouse.storage_location.id,
                }])

                # Change the report extension to PDF
                action_report, = ActionReport.search([
                    ('name', '=', 'Customer Restocking List'),
                    ('report_name', '=',
                     'report.customer_return_restocking_list')
                ])
                action_report.extension = 'pdf'
                action_report.save()

                # Set Pool.test as False as we need the report to be generated
                # as PDF
                # This is specifically to cover the PDF coversion code
                Pool.test = False

                # Generate Customer Restocking List Report
                val = Report.execute([shipment.id], {})

                # Revert Pool.test back to True for other tests to run normally
                Pool.test = True

                self.assertTrue(val)
                # Assert report type
                self.assertEqual(val[0], 'pdf')
                # Assert report name
                self.assertEqual(val[3], 'Customer Restocking List')

    def test_0132_test_product_ledger_report(self):
        """
        Test product ledger report
        """
        LedgerReport = POOL.get('report.product_ledger', type="report")
        Date = POOL.get('ir.date')
        LedgerWizard = POOL.get(
            'product.product.ledger.wizard', type="wizard"
        )
        Location = POOL.get('stock.location')

        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()

            warehouse, = Location.search([('type', '=', 'warehouse')])

            with Transaction().set_context(active_ids=[self.product.id]):

                session_id, start_state, end_state = LedgerWizard.create()

                start_data = {
                    'products': [self.product.id],
                    'warehouses': [warehouse.id],
                    'start_date': Date.today(),
                    'end_date': Date.today(),
                }
                wizard_data = {
                    start_state: start_data,
                }

                result = LedgerWizard.execute(
                    session_id, wizard_data, 'view'
                )
                self.assertEqual(
                    result['actions'][0][1]['products'], [self.product.id]
                )

                self.assertEqual(
                    result['actions'][0][1]['warehouses'], [warehouse.id]
                )
                self.assertEqual(
                    result['actions'][0][1]['start_date'], Date.today()
                )
                self.assertEqual(
                    result['actions'][0][1]['end_date'], Date.today()
                )

                val = LedgerReport.execute([], result['actions'][0][1])

                self.assert_(val)
                # Assert report type
                self.assertEqual(val[0], 'pdf')
                # Assert report name
                self.assertEqual(val[3], 'Product Ledger')

    def test_0130_test_product_ledger_report_data(self):
        """
        Test product ledger report data
        """
        LedgerReport = POOL.get('report.product_ledger', type="report")
        Date = POOL.get('ir.date')
        Location = POOL.get('stock.location')
        StockMove = POOL.get('stock.move')

        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()

            today = Date.today()
            warehouse, = Location.search([('type', '=', 'warehouse')])
            supplier, = Location.search([('type', '=', 'supplier')])
            customer, = Location.search([('type', '=', 'customer')])
            lost_found, = Location.search([('type', '=', 'lost_found')])
            production, = Location.create([{
                'name': 'Production',
                'type': 'production'
            }])

            data = {
                'products': [self.product.id],
                'warehouses': [warehouse.id],
                'start_date': Date.today() - relativedelta(days=15),
                'end_date': Date.today(),
            }

            with Transaction().set_context(company=self.company.id):

                self.sale = self.Sale(
                    party=self.party,
                    invoice_address=self.party.addresses[0],
                    shipment_address=self.party.addresses[0],
                    lines=[],
                )
                self.sale.save()

                sale_line, = self.SaleLine.create([{
                    'type': 'line',
                    'unit_price': 20,
                    'quantity': 1,
                    'description': "Test Sale",
                    'sale': self.sale,
                    'unit': self.uom,
                }])

                # 1. =====Purchases=====
                purchase1, = StockMove.create([{
                    'from_location': supplier.id,
                    'to_location': warehouse.input_location.id,
                    'quantity': 2,
                    'product': self.product,
                    'uom': self.product.default_uom,
                    'unit_price': 20,
                    'effective_date': today - relativedelta(days=10)
                }])
                StockMove.assign([purchase1])
                StockMove.do([purchase1])

                purchase2, = StockMove.create([{
                    'from_location': supplier.id,
                    'to_location': warehouse.input_location.id,
                    'quantity': 1,
                    'product': self.product,
                    'uom': self.product.default_uom,
                    'unit_price': 20,
                    'effective_date': today - relativedelta(days=30)
                }])
                StockMove.assign([purchase2])
                StockMove.do([purchase2])

                purchase3, = StockMove.create([{
                    'from_location': supplier.id,
                    'to_location': warehouse.input_location.id,
                    'quantity': 1,
                    'product': self.product,
                    'uom': self.product.default_uom,
                    'unit_price': 20,
                    'effective_date': today - relativedelta(days=5)
                }])
                StockMove.assign([purchase3])

                purchase4, = StockMove.create([{
                    'from_location': supplier.id,
                    'to_location': warehouse.input_location.id,
                    'quantity': 2,
                    'product': self.product,
                    'uom': self.product.default_uom,
                    'unit_price': 20,
                    'effective_date': today - relativedelta(days=5)
                }])
                StockMove.assign([purchase4])
                StockMove.do([purchase4])

                # 2. ======Productions========
                production1, = StockMove.create([{
                    'from_location': production.id,
                    'to_location': warehouse.input_location.id,
                    'quantity': 2,
                    'product': self.product,
                    'uom': self.product.default_uom,
                    'unit_price': 20,
                    'effective_date': today - relativedelta(days=10)
                }])
                StockMove.assign([production1])
                StockMove.do([production1])

                production2, = StockMove.create([{
                    'from_location': production.id,
                    'to_location': warehouse.input_location.id,
                    'quantity': 1,
                    'product': self.product,
                    'uom': self.product.default_uom,
                    'unit_price': 20,
                    'effective_date': today - relativedelta(days=30)
                }])
                StockMove.assign([production2])
                StockMove.do([production2])

                production3, = StockMove.create([{
                    'from_location': production.id,
                    'to_location': warehouse.input_location.id,
                    'quantity': 1,
                    'product': self.product,
                    'uom': self.product.default_uom,
                    'unit_price': 20,
                    'effective_date': today - relativedelta(days=5)
                }])
                StockMove.assign([production3])

                production4, = StockMove.create([{
                    'from_location': production.id,
                    'to_location': warehouse.input_location.id,
                    'quantity': 2,
                    'product': self.product,
                    'uom': self.product.default_uom,
                    'unit_price': 20,
                    'effective_date': today - relativedelta(days=5)
                }])
                StockMove.assign([production4])
                StockMove.do([production4])

                # 3. ======Customers========
                customer1, = StockMove.create([{
                    'origin': '%s, %d' % (sale_line.__name__, sale_line.id),
                    'from_location': warehouse.input_location.id,
                    'to_location': customer.id,
                    'quantity': 2,
                    'product': self.product,
                    'uom': self.product.default_uom,
                    'unit_price': 20,
                    'effective_date': today - relativedelta(days=10)
                }])
                StockMove.assign([customer1])
                StockMove.do([customer1])

                customer2, = StockMove.create([{
                    'origin': '%s, %d' % (sale_line.__name__, sale_line.id),
                    'from_location': warehouse.input_location.id,
                    'to_location': customer.id,
                    'quantity': 1,
                    'product': self.product,
                    'uom': self.product.default_uom,
                    'unit_price': 20,
                    'effective_date': today - relativedelta(days=30)
                }])
                StockMove.assign([customer2])
                StockMove.do([customer2])

                customer3, = StockMove.create([{
                    'origin': '%s, %d' % (sale_line.__name__, sale_line.id),
                    'from_location': warehouse.input_location.id,
                    'to_location': customer.id,
                    'quantity': 1,
                    'product': self.product,
                    'uom': self.product.default_uom,
                    'unit_price': 20,
                    'effective_date': today - relativedelta(days=5)
                }])
                StockMove.assign([customer3])

                customer4, = StockMove.create([{
                    'origin': '%s, %d' % (sale_line.__name__, sale_line.id),
                    'from_location': warehouse.input_location.id,
                    'to_location': customer.id,
                    'quantity': 2,
                    'product': self.product,
                    'uom': self.product.default_uom,
                    'unit_price': 20,
                    'effective_date': today - relativedelta(days=5)
                }])
                StockMove.assign([customer4])
                StockMove.do([customer4])

                # 4. =====Lost And Founds========
                lost_found1, = StockMove.create([{
                    'from_location': lost_found.id,
                    'to_location': warehouse.input_location.id,
                    'quantity': 2,
                    'product': self.product,
                    'uom': self.product.default_uom,
                    'unit_price': 20,
                    'effective_date': today - relativedelta(days=10)
                }])
                StockMove.assign([lost_found1])
                StockMove.do([lost_found1])

                lost_found2, = StockMove.create([{
                    'from_location': lost_found.id,
                    'to_location': warehouse.input_location.id,
                    'quantity': 1,
                    'product': self.product,
                    'uom': self.product.default_uom,
                    'unit_price': 20,
                    'effective_date': today - relativedelta(days=30)
                }])
                StockMove.assign([lost_found2])
                StockMove.do([lost_found2])

                lost_found3, = StockMove.create([{
                    'from_location': lost_found.id,
                    'to_location': warehouse.input_location.id,
                    'quantity': 1,
                    'product': self.product,
                    'uom': self.product.default_uom,
                    'unit_price': 20,
                    'effective_date': today - relativedelta(days=5)
                }])
                StockMove.assign([lost_found3])

                lost_found4, = StockMove.create([{
                    'from_location': lost_found.id,
                    'to_location': warehouse.input_location.id,
                    'quantity': 2,
                    'product': self.product,
                    'uom': self.product.default_uom,
                    'unit_price': 20,
                    'effective_date': today - relativedelta(days=5)
                }])
                StockMove.assign([lost_found4])
                StockMove.do([lost_found4])

                # 5. =====Consumed========
                consumed1, = StockMove.create([{
                    'from_location': warehouse.input_location.id,
                    'to_location': production.id,
                    'quantity': 2,
                    'product': self.product,
                    'uom': self.product.default_uom,
                    'unit_price': 20,
                    'effective_date': today - relativedelta(days=10)
                }])
                StockMove.assign([consumed1])
                StockMove.do([consumed1])

                consumed2, = StockMove.create([{
                    'from_location': warehouse.input_location.id,
                    'to_location': production.id,
                    'quantity': 1,
                    'product': self.product,
                    'uom': self.product.default_uom,
                    'unit_price': 20,
                    'effective_date': today - relativedelta(days=30)
                }])
                StockMove.assign([consumed2])
                StockMove.do([consumed2])

                consumed3, = StockMove.create([{
                    'from_location': warehouse.input_location.id,
                    'to_location': production.id,
                    'quantity': 1,
                    'product': self.product,
                    'uom': self.product.default_uom,
                    'unit_price': 20,
                    'effective_date': today - relativedelta(days=5)
                }])
                StockMove.assign([consumed3])

                consumed4, = StockMove.create([{
                    'from_location': warehouse.input_location.id,
                    'to_location': production.id,
                    'quantity': 2,
                    'product': self.product,
                    'uom': self.product.default_uom,
                    'unit_price': 20,
                    'effective_date': today - relativedelta(days=5)
                }])
                StockMove.assign([consumed4])
                StockMove.do([consumed4])

                purchases = LedgerReport.get_purchases(self.product.id, data)

                productions = LedgerReport.get_productions(
                    self.product.id, data
                )

                customers = LedgerReport.get_customers(self.product.id, data)

                lost_and_founds = LedgerReport.get_lost_and_founds(
                    self.product.id, data
                )

                consumed = LedgerReport.get_consumed(self.product.id, data)

                # Purchase2 ( assigned ) and  purchase3 ( effective_date <
                # start_date) are ignored
                self.assertEqual(len(purchases), 2)

                # Production2 ( assigned ) and production3 ( effective_date <
                # start_date) are ignored
                self.assertEqual(len(productions), 2)

                # Customer2 ( assigned ) and customer3 ( effective_date <
                # start_date) are ignored
                self.assertEqual(len(customers), 2)

                # lost_found2 ( assigned ) and lost_found3 ( effective_date <
                # start_date) are ignored
                self.assertEqual(len(lost_and_founds), 2)

                # consumed2 ( assigned ) and consumed3 ( effective_date <
                # start_date) are ignored
                self.assertEqual(len(consumed), 2)

                record = {
                    'purchases': purchases,
                    'productions': productions,
                    'customers': customers,
                    'lost_and_founds': lost_and_founds,
                    'consumed': consumed,
                    'product': self.product,
                }

                # Get summary
                result = LedgerReport.get_summary(record, data)

                self.assertEqual(result['purchased'], 4)
                self.assertEqual(result['produced'], 4)
                self.assertEqual(result['consumed'], 4)
                self.assertEqual(result['lost'], 4)
                self.assertEqual(result['customer'], 4)

                self.assertEqual(result['opening_stock'], 1)
                self.assertEqual(result['closing_stock'], 5)

    @unittest.skipIf(sys.platform == 'darwin', 'wkhtmltopdf repo on OSX')
    def test_0110_test_consolidate_picking_list_report(self):
        """
        Test ConsolidatedPickingList
        """
        Report = POOL.get('report.consolidated_picking_list', type="report")
        Date = POOL.get('ir.date')
        ActionReport = POOL.get('ir.action.report')

        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()

            with Transaction().set_context({'company': self.company.id}):
                shipment, = self.ShipmentOut.create([{
                    'planned_date': Date.today(),
                    'effective_date': Date.today(),
                    'customer': self.party.id,
                    'warehouse': self.StockLocation.search([
                        ('type', '=', 'warehouse')
                    ])[0],
                    'delivery_address': self.party.addresses[0],
                }])
                move1, = self.Move.create([{
                    'shipment': ('stock.shipment.out', shipment.id),
                    'product': self.product.id,
                    'uom': self.uom.id,
                    'quantity': 6,
                    'from_location': shipment.warehouse.storage_location.id,
                    'to_location': shipment.warehouse.output_location.id,
                }])

                # Change the report extension to PDF
                action_report, = ActionReport.search([
                    ('name', '=', 'Consolidated Picking List'),
                    ('report_name', '=', 'report.consolidated_picking_list')
                ])
                action_report.extension = 'pdf'
                action_report.save()

                # Set Pool.test as False as we need the report to be generated
                # as PDF
                # This is specifically to cover the PDF coversion code
                Pool.test = False

                # Generate Consolidated List Report
                val = Report.execute([shipment.id], {})

                # Revert Pool.test back to True for other tests to run normally
                Pool.test = True

                self.assertTrue(val)
                # Assert report type
                self.assertEqual(val[0], 'pdf')
                # Assert report name
                self.assertEqual(val[3], 'Consolidated Picking List')

    @unittest.skipIf(sys.platform == 'darwin', 'wkhtmltopdf repo on OSX')
    def test_0110_test_delivery_note_report(self):
        """
        Test Deliver Note
        """
        Report = POOL.get('report.delivery_note', type="report")
        Date = POOL.get('ir.date')
        ActionReport = POOL.get('ir.action.report')

        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()

            with Transaction().set_context({'company': self.company.id}):
                shipment, = self.ShipmentOut.create([{
                    'planned_date': Date.today(),
                    'effective_date': Date.today(),
                    'customer': self.party.id,
                    'warehouse': self.StockLocation.search([
                        ('type', '=', 'warehouse')
                    ])[0],
                    'delivery_address': self.party.addresses[0],
                }])
                move1, = self.Move.create([{
                    'shipment': ('stock.shipment.out', shipment.id),
                    'product': self.product.id,
                    'uom': self.uom.id,
                    'quantity': 6,
                    'from_location': shipment.warehouse.storage_location.id,
                    'to_location': shipment.warehouse.output_location.id,
                }])

                # Change the report extension to PDF
                action_report, = ActionReport.search([
                    ('name', '=', 'Delivery Note'),
                    ('report_name', '=', 'report.delivery_note')
                ])
                action_report.extension = 'pdf'
                action_report.save()

                # Set Pool.test as False as we need the report to be generated
                # as PDF
                # This is specifically to cover the PDF coversion code
                Pool.test = False

                # Generate Delivery List Report
                val = Report.execute([shipment.id], {})

                # Revert Pool.test back to True for other tests to run normally
                Pool.test = True

                self.assertTrue(val)
                # Assert report type
                self.assertEqual(val[0], 'pdf')
                # Assert report name
                self.assertEqual(val[3], 'Delivery Note')


def suite():
    "Define suite"
    test_suite = trytond.tests.test_tryton.suite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestShipment)
    )
    return test_suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
