import unittest
import datetime
import time
from Cards import Cards
from Orders import Orders
from Payments import Payments
import config


class Test(unittest.TestCase):

    config.api_key = '4168A8A476B84DBCAF409C24F379BAC5'
    config.environment = 'production'

    def setUp(self):
        self.timestamp = int(time.mktime(datetime.datetime.timetuple(datetime.datetime.now())))
        self.order1 = Orders.create(order_id=self.timestamp, amount=1000)
        self.assertIsInstance(self.order1, Orders.Order)
        self.assertEqual(self.order1.status, "CREATED")
        self.order2 = Orders.create(order_id=self.timestamp + 1, amount=1000)

    def test__orders(self):

        # Test for get_status
        status = Orders.get_status(order_id=self.timestamp)
        self.assertIsInstance(status, Orders.Order)
        self.assertEqual(float(status.order_id), self.timestamp)

        # Test for list
        order_list = Orders.list()
        self.assertIsNotNone(order_list)
        for order in order_list:
            self.assertIsInstance(order, Orders.Order)

        # Test for update
        updated_order = Orders.update(order_id=self.timestamp, amount=500)
        status = Orders.get_status(order_id=self.timestamp)
        self.assertEqual(status.amount, updated_order.amount)

        # Test for refund

    @staticmethod
    def delete_all_cards():
        card_list = Cards.list(customer_id='user')
        for card in card_list:
            Cards.delete(card_token=card.token)

    def test__cards(self):

        # Test for add
        card = Cards.add(merchant_id='shreyas', customer_id="user", customer_email='abc@xyz.com',
                                card_number=str(int(self.timestamp)*(10**6)), card_exp_year='20', card_exp_month='12')
        self.assertIsNotNone(card.reference)
        self.assertIsNotNone(card.token)
        self.assertIsNotNone(card.fingerprint)

        # Test for delete
        deleted_card = Cards.delete(card_token=card.token)
        self.assertTrue(deleted_card.deleted)

        # Test for list
        Test.delete_all_cards()
        Cards.add(merchant_id='shreyas', customer_id="user", customer_email='abc@xyz.com',
                         card_number=str(int(self.timestamp) * (10 ** 6)), card_exp_year='20', card_exp_month='12')
        Cards.add(merchant_id='shreyas', customer_id="user", customer_email='abc@xyz.com',
                         card_number=str((int(self.timestamp)+1) * (10 ** 6)), card_exp_year='20', card_exp_month='12')
        card_list = Cards.list(customer_id='user')
        self.assertIsNotNone(card_list)
        self.assertEqual(len(card_list), 2)
        Test.delete_all_cards()

    def test__payments(self):

        # Test for create_card_payment
        payment = Payments.create_card_payment(order_id=self.order1.order_id,
                                                      merchant_id='shreyas',
                                                      payment_method_type='CARD',
                                                      card_token='68d6b0c6-6e77-473f-a05c-b460ef983fd8',
                                                      redirect_after_payment=False,
                                                      format='json',
                                                      card_number='5243681100075285',
                                                      name_on_card='Customer',
                                                      card_exp_year='20',
                                                      card_exp_month='12', card_security_code='123',
                                                      save_to_locker=False)
        self.assertIsNotNone(payment.txn_id)
        self.assertEqual(payment.status, 'PENDING_VBV')

        # Test for create_net_banking_payment
        payment = Payments.create_net_banking_payment(order_id=self.order2.order_id,
                                                             merchant_id='shreyas',
                                                             payment_method_type='NB',
                                                             payment_method='NB_HDFC',
                                                             redirect_after_payment=False,
                                                             format='json')
        self.assertIsNotNone(payment.txn_id)
        self.assertEqual(payment.status, 'PENDING_VBV')

if __name__ == '__main__':
    unittest.main()
