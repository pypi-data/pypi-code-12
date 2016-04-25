from django.db import models
from django.conf import settings
from django.db.models import get_model
from django.core.exceptions import ImproperlyConfigured

"""We now allow a pluggable Order models that might
 look a little something like this:

from django.contrib.auth.models import User
from mauveinternet.ordering.picklefield import PickleField
from mauveinternet.ordering.order import OrderItemList
from mauveinternet.ordering.orderbase import OrderBase, STATUS_OPTIONS

# If you want column-level database encryption for your orders
from mauveinternet.ordering.lockbox import Lockable

class Order(models.Model, OrderBase):
        status = models.CharField(max_length=1, choices=STATUS_OPTIONS, default='N')

        customer = models.ForeignKey(User)
        date_placed = models.DateTimeField(auto_now_add=True)

        vat_number = models.CharField(max_length=24, blank=True)

        billing_address = models.TextField()
        billing_postcode = models.CharField('Postcode', max_length=10)

        items = PickleField(OrderItemList)

        total = models.DecimalField(editable=False, max_digits=10, decimal_places=2)

"""

def get_order_model():
    model_class = get_model(*settings.ORDER_MODEL.split('.'))
    if model_class is None:
        raise ImproperlyConfigured("No ORDER_MODEL found for '%s'" % settings.ORDER_MODEL)
    return model_class


def get_status_options():
    return get_order_model()._meta.get_field('status').choices


class OrderStatusChange(models.Model):
    order = models.ForeignKey(get_order_model())
    date = models.DateTimeField(auto_now_add=True)
    previous_status = models.CharField(max_length=1, choices=get_status_options() + [('-', '-')])
    message = models.CharField(max_length=255)

    def new_status(self):
        try:
            return self.order.orderstatuschange_set.filter(date__gt=self.date).order_by('date')[0].previous_status
        except IndexError:
            return self.order.status

    def get_new_status_display(self):
        s=self.new_status()
        disps=dict(get_status_options()+[('-', '-')])
        return disps[s]

    class Meta:
        # Nowhere better for this to go
        permissions = [('can_view_orders', 'Permission to view orders')]
