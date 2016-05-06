import json

from django.db import models
from django.core.cache import cache

from jsonfield import JSONField
from jsonfield.utils import default as encoder_default

from postnl_checkout.exceptions import PostNLResponseException

from .settings import postnl_checkout_settings as settings
from .utils import get_client


class PostNLJSONEncoder(json.JSONEncoder):
    """ Encoder with default allowing encoding of datetime objects. """
    def default(self, o):
        return encoder_default(o)


# Instantiate a client
postnl_client = get_client()


class Order(models.Model):
    """ Django model representing the result of the ReadOrder call. """

    # Primary identifier
    order_token = models.CharField(max_length=255, primary_key=True)

    # Other indexe fields
    order_ext_ref = models.CharField(db_index=True, max_length=255)
    order_date = models.DateField(db_index=True)
    customer_ext_ref = models.CharField(db_index=True, max_length=255)

    # Raw data
    prepare_order_request = JSONField(encoder_class=PostNLJSONEncoder)
    prepare_order_response = JSONField(encoder_class=PostNLJSONEncoder)

    read_order_response = JSONField(encoder_class=PostNLJSONEncoder)

    update_order_request = JSONField(encoder_class=PostNLJSONEncoder)

    @classmethod
    def prepare_order(cls, **kwargs):
        """ Call PrepareOrder and create Order using resulting token. """

        # Assert required attributes
        assert 'Order' in kwargs

        order_data = kwargs['Order']

        assert 'ExtRef' in order_data
        assert 'OrderDatum' in order_data

        # Call API
        response = postnl_client.prepare_order(**kwargs)

        assert 'Checkout' in response
        assert 'OrderToken' in response['Checkout']
        order_token = response['Checkout']['OrderToken']

        # Store data
        order = cls(
            order_token=order_token,
            order_ext_ref=order_data['ExtRef'],
            order_date=order_data['OrderDatum'],
            prepare_order_request=kwargs,
            prepare_order_response=response
        )

        # Validate and save
        order.clean()
        order.save()

        return order

    @classmethod
    def ping_status(cls):
        """ Wrap PingStatus for ease of accesibility. """

        if settings.SERVICE_STATUS_CACHE_TIMEOUT:
            status = cache.get(settings.SERVICE_STATUS_CACHE_KEY, None)
            if status is None:
                status = postnl_client.ping_status()

                cache.set(
                    settings.SERVICE_STATUS_CACHE_KEY, status,
                    settings.SERVICE_STATUS_CACHE_TIMEOUT
                )
        else:
            # No timeout, don't cache
            status = postnl_client.ping_status()

        return status

    def read_order(self):
        """ Call ReadOrder and store results. """
        assert self.order_token

        # Prepare arguments
        kwargs = {
            'Checkout': {
                'OrderToken': self.order_token
            }
        }

        # Call API
        response = postnl_client.read_order(**kwargs)

        # Store response
        self.read_order_response = response
        self.clean()
        self.save()

        # Return updated instance
        return self

    def confirm_order(self, **kwargs):
        """ Call ConfirmOrder and confirm results. """

        # Prepare arguments
        assert not 'Checkout' in kwargs

        kwargs['Checkout'] = {
            'OrderToken': self.order_token
        }

        # Call API
        result = postnl_client.confirm_order(**kwargs)

        # Make sure the result is sensible
        if result['Order']['ExtRef'] != self.order_ext_ref:
            raise Exception('Order reference does not correspond.')

    def update_order(self, **kwargs):
        """ Call UpdateOrder, store request and confirm results. """

        # Prepare arguments
        assert not 'Checkout' in kwargs

        kwargs['Checkout'] = {
            'OrderToken': self.order_token
        }

        # Call API
        response = postnl_client.update_order(**kwargs)

        assert response in (True, False)

        if not response:
            raise PostNLResponseException('Could not update order.')

        # Store request
        self.update_order_request = kwargs
        self.clean()
        self.save()

        # Return updated instance
        return self
