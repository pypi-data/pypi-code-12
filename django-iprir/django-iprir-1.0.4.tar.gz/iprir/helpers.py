"""
helpers for ip registry (iprir) project

useful functions to query iprir database
"""

from .models import TLD, InetNum
from .utils import ip2int, int2ip


def print_meta(request):

    """
    print request.META dictionary
    """

    for key, value in request.META.items():
        if key.startswith('CONTENT'):
            print(key, ' --> ', value)


def find_inetnum(ip_address):

    """
    find inetnum record of IP address
    """

    ipnumclass = ip2int(ip_address.split('.')[0]+'.0.0.0')
    ipnumfull = ip2int(ip_address)

    inetnum = InetNum.objects.filter(
        inetNumFrom__gte=ipnumclass, inetNumFrom__lte=ipnumfull
    ).order_by('inetNumFrom').last()

    return inetnum


def ip_info(request, ip_address=None):

    """
    returns dictionary with information about IP address
    """

    inetnum = find_inetnum(ip_address if ip_address else request.META.get('REMOTE_ADDR'))

    if inetnum:
        context = {
            'registry': str(inetnum.registry),
            'tld': str(inetnum.tld),
            'InetNumfrom': inetnum.inetNumIPFrom,
            'InetNumto': int2ip(inetnum.inetNumTo),
            'valid': inetnum.inetNumValid,
            'allocated': inetnum.inetNumAllocated,
            'modified': inetnum.lastModified.strftime("%d/%m/%y %H:%M"),
        }
    else:
        context = {
            'registry': None,
            'tld': None,
            'InetNumfrom': '0.0.0.0',
            'InetNumto': '255.255.255.255',
            'valid': False,
            'allocated': False,
        }

    context['remote_addr'] = request.META.get('REMOTE_ADDR') if not ip_address else ip_address

    return context
