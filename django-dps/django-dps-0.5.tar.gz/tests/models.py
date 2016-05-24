from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

from dps.models import BasicTransactionProtocol, Transaction


class Payment(models.Model, BasicTransactionProtocol):
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def get_amount(self):
        return self.amount

    transactions = GenericRelation(Transaction)
