# -*- coding: utf-8 -*-
"""
    carrier

    :copyright: (c) 2015 by Fulfil.IO Inc.
    :license: see LICENSE for details.
"""
from trytond.pool import PoolMeta
from nereid import current_app
from trytond.exceptions import UserError

__metaclass__ = PoolMeta
__all__ = ['Carrier']


class Carrier:
    __name__ = 'carrier'

    @classmethod
    def _website_carrier_domain(cls):
        """This method returns domain to filter shipping carriers for website

        Downstream modules can inherit and update customize this domain.
        """
        return []

    @classmethod
    def get_rate_list(cls):
        """
        Return list of tuples as:
            [
                (
                    <display method name>, <rate>, <currency>, <metadata>,
                    <write_vals>
                )
                ...
            ]
        """
        carriers = cls.search(cls._website_carrier_domain())
        errors = []
        rate_list = []
        for carrier in carriers:
            try:
                rate_list += carrier.get_rates()
            except UserError, e:
                # This error will only come when address is invalid
                errors.append(e.message)
            except:
                # Several other errors can come from third party service.
                #
                # Send error log to sentry for debugging, but don't stop user
                # from checkout
                sentry_client = current_app.extensions.get('sentry')

                if sentry_client:
                    sentry_client.captureException(
                        True, tags={"error": "Shipping Error Logs"}
                    )
                else:
                    raise
        if not rate_list and errors:
            raise cls.raise_user_error('\n'.join(errors))
        return rate_list
