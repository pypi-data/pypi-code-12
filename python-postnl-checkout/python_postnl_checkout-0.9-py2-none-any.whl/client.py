import logging
logger = logging.getLogger(__name__)

import hashlib
import datetime
import decimal

import requests

import suds

import suds_requests

from .exceptions import PostNLRequestException, PostNLResponseException
from .utils import contains_any


class PostNLCheckoutClient(object):
    """
    Client exposing the PostNL checkout client.

    This part should not depend on Django in any way and might be separated
    from the rest of the module later.
    """

    SANDBOX_ENDPOINT_URL = (
        'https://testservice.postnl.com/CIF_SB/'
        'WebshopCheckoutWebService/2_2/WebshopCheckoutService.svc?wsdl'
    )

    PRODUCTION_ENDPOINT_URL = (
        'https://service.postnl.com/CIF/'
        'WebshopCheckoutWebService/2_2/WebshopCheckoutService.svc?wsdl'
    )

    # PostNL date/time format
    datetime_format = '%d-%m-%Y %H:%M:%S'

    # Monetary fields to convert
    monetary_fields = (
        'Prijs', 'Kosten', 'Subtotaal', 'VerzendKosten', 'PaymentTotal'
    )

    def __init__(
        self, username, password, webshop_id, environment,
        timeout=None, cache=None
    ):
        """
        Initialize, setting required attributes and instantiate web service.
        """
        self.webshop_id = webshop_id

        # Setup Requests session
        session = self._get_session(timeout)

        # Instantiate web service.
        self.suds_client = self._get_client(
            environment, session, username, password, cache
        )

        self.service = self.suds_client.service

    @classmethod
    def _get_session(cls, timeout=None):
        """ Setup requests session. """
        session = requests.Session()
        session.verify = True

        if timeout:
            session.timeout = timeout

        return session

    @classmethod
    def _get_client(
        cls, environment, session, username, password, cache=None
    ):
        """ Return webservice from SOAP client (suds). """

        # Endpoint URL depending on environment
        assert environment in ('sandbox', 'production'), 'Unknown environment'

        if environment == 'production':
            webservice_url = cls.PRODUCTION_ENDPOINT_URL
        else:
            webservice_url = cls.SANDBOX_ENDPOINT_URL

        # Setup authentication
        sha1 = hashlib.sha1()
        sha1.update(password)

        security = suds.wsse.Security()
        token = suds.wsse.UsernameToken(username, sha1.hexdigest())
        security.tokens.append(token)

        # Instantiate client
        client = suds.client.Client(
            webservice_url,
            transport=suds_requests.RequestsTransport(session),
            cachingpolicy=1, cache=cache,
            wsse=security
        )

        return client

    @classmethod
    def _parse_datetime(cls, value):
        """ Parse datetime in PostNL format. """

        return datetime.datetime.strptime(value, cls.datetime_format)

    @classmethod
    def _format_datetime(cls, value):
        """ Format datetime in PostNL format. """

        return datetime.datetime.strftime(value, cls.datetime_format)

    @classmethod
    def _assert_required_attributes(cls, kwargs, required):
        """ Assert whether all required attributes are present. """

        for key in required:
            assert key in kwargs, 'Required argument %s not present.' % key

    @classmethod
    def _sudsobject_to_dict(cls, obj, wrapper=None, key=''):
        """
        Recursively convert a (suds) dict-ish object to a dictionary,
        optionally mapping values through the wrapper function.

        Inspired by: http://www.snip2code.com/Snippet/15899/convert-suds-response-to-dictionary
        """
        if not wrapper:
            # Default wrapper to a no-op
            # Note: this is not a great idea performance-wise
            wrapper = lambda k, v: v

        if hasattr(obj, 'items'):
            # Dictionary
            iterator = obj.items()
        elif hasattr(obj, '__keylist__'):
            # Suds object
            iterator = obj
        else:
            # Object is not dictionary-like, return wrapped value
            return wrapper(key, obj)

        # Object is dictionary-like, potentially recurse

        out = {}
        for key, value in iterator:
            if isinstance(value, list):
                # Value is list
                out[key] = []
                for item in value:
                    out[key].append(
                        cls._sudsobject_to_dict(item, wrapper, key)
                    )
            else:
                # Attempt recursion
                out[key] = cls._sudsobject_to_dict(value, wrapper, key)

        return out

    @classmethod
    def _from_python(cls, obj):
        """ Convert object from Pythonic format to API format. """

        def wrapper(key, value):
            """ Wrapper used to convert values. """
            # Leave None in place
            if value is None:
                return None

            # Convert dates
            if 'Datum' in key:
                return unicode(cls._format_datetime(value))

            # Default; convert to strings
            return unicode(value)

        obj = cls._sudsobject_to_dict(obj, wrapper)

        return obj

    @classmethod
    def _to_python(cls, obj):
        """ Convert object from API format to Pythonic format. """

        def wrapper(key, value):
            """ Wrapper used to convert values. """

            # Leave None in place
            if value is None:
                return None

            # Convert dates
            if 'Datum' in key:
                return cls._parse_datetime(value)

            # Convert monetary amounts to Decimal
            if contains_any(key, cls.monetary_fields):
                return decimal.Decimal(value)

            # Return string version of value
            return unicode(value)

        obj = cls._sudsobject_to_dict(obj, wrapper)

        return obj

    def _add_webshop(self, kwargs):
        """ Add webshop to argument dictionary. """

        assert 'Webshop' not in kwargs
        kwargs['Webshop'] = {
            'IntRef': self.webshop_id
        }

    def _api_call(self, method_name, **kwargs):
        """ Wrapper for API calls. """

        # Get relevant method
        method = getattr(self.service, method_name)

        # Convert arguments from Pythonic formats
        kwargs = self._from_python(kwargs)

        try:
            # Perform API call
            result = method(**kwargs)

        except suds.WebFault, e:
            # Catch CIF Exception details and re-raise

            # Get error message
            error = e.fault.detail.CifException.Errors.ExceptionData.ErrorMsg
            raise PostNLRequestException(error)

        # Convert result to Pythonic formats
        result = self._to_python(result)

        return result

    def prepare_order(self, **kwargs):
        """ Wrapper around PrepareOrder API call. """

        # Add webshop before executing request
        self._add_webshop(kwargs)

        if __debug__:
            self._assert_required_attributes(
                kwargs, ('Webshop', 'Order')
            )

        # Execute API call
        return self._api_call('PrepareOrder', **kwargs)

    def read_order(self, **kwargs):
        """ Wrapper around ReadOrder API call. """

        # Add webshop before executing request
        self._add_webshop(kwargs)

        if __debug__:
            self._assert_required_attributes(
                kwargs, ('Webshop', 'Checkout')
            )

        # Execute API call
        return self._api_call('ReadOrder', **kwargs)

    def confirm_order(self, **kwargs):
        """ Wrapper around ConfirmOrder API call. """

        # Add webshop before executing request
        self._add_webshop(kwargs)

        if __debug__:
            self._assert_required_attributes(
                kwargs, ('Webshop', 'Checkout', 'Order')
            )

        # Execute API call
        result = self._api_call('ConfirmOrder', **kwargs)

        # Make sure the response is sensible
        if not 'Order' in result and 'ExtRef' in result['Order']:
            raise PostNLResponseException('No order reference in result.')

        # Return the result
        return result

    def update_order(self, **kwargs):
        """ Wrapper around UpdateOrder API call. """

        # Add webshop before executing request
        self._add_webshop(kwargs)

        if __debug__:
            self._assert_required_attributes(
                kwargs, ('Webshop', 'Order')
            )

        # Execute API call
        result = self._api_call('UpdateOrder', **kwargs)

        # Return the result
        assert result in ('true', 'false')

        return result == 'true'

    def ping_status(self, **kwargs):
        """
        Wrapper around PingStatus API call.

        Returns True if service OK, False for not OK.
        """

        # Execute API call
        result = self._api_call('PingStatus')

        assert result in ('OK', 'NOK')

        return result == 'OK'
