"""
We call all this guessing as there are no certainties.
The client could be using a proxy or vpn or there may be something going on at
the hosting provider that influences the result.

So data from here should be treated as a default that the user can override
where necessary.
"""
import os
from functools import lru_cache
import ipware.ip
from . import fetch

@lru_cache(maxsize=8)
def ipaddress(request=None):
    """Return an IP Address from the request,
    or G11N_IP_OVERRIDE environment variable if that is set."""
    override = None
    key = 'G11N_IP_OVERRIDE'
    if key in os.environ:
        override = os.environ[key]

    if override is None and request is None:
        text = "Environment variable %s must be set to an appropriate IP."
        raise ValueError(text)

    if request is None:
        value = override
    else:
        value = ipware.ip.get_ip(request)

    return {'ip':value}

def guess_country(request):
    "Guess the country from the request (using the IP address)."
    ip_address = ipaddress(request)['ip']
    return {'country':fetch.country_by_ip(ip_address)}

def guess_language(request):
    "Guess the language from the request (using the browser headers)."
    return {'language':request.LANGUAGE_CODE}

def guess_currency(request):
    "Guess the currency from the request (via guess_country)."
    tld = guess_country(request)['country']
    return {'currency':fetch.currency_by_country_tld(tld)}

def guess_country_language_currency(request):
    "Guess all of these in a single function."
    functions = [guess_country, guess_language, guess_currency, ipaddress]
    tmp = dict()
    for function in functions:
        for key, value in function(request).items():
            tmp[key] = value
    return tmp
