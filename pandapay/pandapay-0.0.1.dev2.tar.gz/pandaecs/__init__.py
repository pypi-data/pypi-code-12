from stripe import Charge
from stripe.resource import convert_to_stripe_object, populate_headers

import stripe

import sys
current_module = sys.modules[__name__]

api_key = None
api_base = 'https://api.pandapay.io'

class AuthenticationError(Exception):
    pass

class APIError(stripe.error.APIError):
    pass

class APIRequestor(stripe.api_requestor.APIRequestor):
    def request(self, *args, **kwargs):
        try:
            return super(APIRequestor, self).request(*args, **kwargs)
        except stripe.error.APIError as e:
            raise APIError(e.message, e.http_body, e.http_status, e.json_body)

class StripeCharge(Charge):
    @classmethod
    def create(cls, api_key=None, idempotency_key=None,
               stripe_account=None, **params):
        api_key_to_use = api_key or current_module.api_key

        if not api_key_to_use:
            raise AuthenticationError('No API key provided. (HINT: set your API key using '
                                      '"pandaecs.api_key = <PANDA_SECRET-KEY>"). You can find your API Keys '
                                      'on the the PandaPay web interface.  See '
                                      'https://www.pandapay.io/docs/api-reference for details, or email '
                                      'support@pandapay.io if you have any questions.')


        requestor = APIRequestor(
            api_key_to_use,
            account=stripe_account,
            api_base=api_base
        )

        url = cls.class_url()
        headers = populate_headers(idempotency_key)

        params_to_use = dict()
        stripe_params = dict(params)

        params_to_use['donation_amount'] = stripe_params.pop('donation_amount', None)
        params_to_use['destination'] = stripe_params.pop('destination_ein', None)
        params_to_use['receipt_email'] = stripe_params.pop('receipt_email', None)
        params_to_use['currency'] = stripe_params.get('currency', None)
        params_to_use['stripe_params'] = stripe_params

        response, returned_api_key = requestor.request('post', url, params_to_use, headers)

        import pdb; pdb.set_trace()

        return StripeCharge.construct_from(response, api_key_to_use, stripe_account)

    @classmethod
    def class_url(cls):
        return '/v1/donations'

    @classmethod
    def construct_from(cls, resp, api_key, stripe_account):
        panda_charge = cls(resp['id'], api_key, stripe_account)

        for k, v in resp.iteritems():
            if k == 'stripe_response':
                next

            panda_charge.__setitem__(k, v)

        panda_charge.original_charge = Charge.construct_from(
            resp.get('stripe_response', {}),
            api_key,
            stripe_account
        )

        return panda_charge

