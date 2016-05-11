"""
We call all this guessing as there are no certainties.
The client could be using a proxy or vpn or there may be something going on at
the hosting provider that influences the result.

So data from here should be treated as a default that the user can override
where necessary.
"""
from functools import lru_cache
import ipware.ip
from . import fetch

@lru_cache(maxsize=8)
def ipaddress(request):
    "Return an IP Address from the request."
    return {'ip':ipware.ip.get_ip(request)}

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
    functions = [guess_country, guess_language, guess_currency]
    tmp = dict()
    for function in functions:
        for key, value in function(request).items():
            tmp[key] = value
    return tmp
