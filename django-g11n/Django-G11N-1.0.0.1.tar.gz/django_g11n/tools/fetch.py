"""
Fetch data.
"""
import ipaddress
from . import models

def country_by_ip(ip_address):
    "Return the TLD assigned to the address block the IP address is part of."
    address = ipaddress.ip_address(ip_address)
    hex_address = hex(int(address))[2::].zfill(32)

    model = models.ALL['IPRange']
    value = model.objects.filter(ipv=address.version,
                                 network_hex__lt=hex_address,
                                 broadcast_hex__gt=hex_address)

    count = value.count()
    if count < 1:
        return None
    elif count > 1:
        text = '! IPCountry table inconsistent on address %s' % ip_address
        raise ValueError(text)
    else:
        return value[0].tld


def currency_by_country_tld(tld):
    "Return the currency data by the top level domain."
    query = models.ALL['Currency'].objects.filter(reference__code_2=tld)
    count = query.count()

    if count >= 1:
        return query[0].code




