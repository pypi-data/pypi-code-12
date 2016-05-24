import requests

from django.test import TestCase, RequestFactory
from django.utils.six import text_type
from dps.transactions import make_payment
from dps.models import Transaction

from .models import Payment


class DpsTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_interactive(self):
        amount = 112.45
        payment = Payment.objects.create(amount=amount)

        request = self.factory.get('/', HTTP_HOST='localhost:8000')
        response = make_payment(payment, request=request)
        self.assertEqual(response.status_code, 302)
        response = requests.get(response['Location'])

        # check the dps page looks approximately correct
        self.assertIn('Payment Checkout', response.text)
        self.assertIn(text_type(amount), response.text)

    def test_recurring(self):
        pass

    def test_status_update(self):
        payment = Payment.objects.create(amount=1)

        trans = Transaction.objects.create(content_object=payment,
                                           status=Transaction.PROCESSING)

        self.assertEqual(trans.complete_transaction(True), True)
        self.assertEqual(trans.status, Transaction.SUCCESSFUL)

        # complete_transaction should only return True once
        self.assertEqual(trans.complete_transaction(True), False)

        # and shouldn't change once done
        self.assertEqual(trans.complete_transaction(False), False)
        self.assertEqual(trans.status, Transaction.SUCCESSFUL)
