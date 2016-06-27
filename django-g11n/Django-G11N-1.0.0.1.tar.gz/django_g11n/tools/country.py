"""
Get Country data, we use the django_countries app to fetch the data.
The app just uses a manually fetched data from the ISO site, since they already
have that coded down I am not repeating that here, even though I have to go to
some troubles recombining it.
"""
from collections import defaultdict
from django_countries import data

ADDITIONS = [[9995, 'CB', 'CBN', False, 'Caribbean'],
             [9996, 'AP', 'APA', False, 'Asia and Pacific'],
             [9997, 'EU', 'EUR', False, 'Europe', 'European Union'],
             [9998, 'ZZ', 'ZZR', False, 'IETF Reserved'],
             [9999, '??', '???', False, 'Unknown']]

def get():
    """Reconstruct the ISO 3166 data, returns a list of row where each row is:
    - Country numeric code
    - Two letter code
    - Three letter code
    - Boolean if it is ISO 3166 (False if it is a local override.
    - Default label of the country
    - Additional label of the country
    Note that there may be multiple additional labels at the end.
    """
    tmp = defaultdict(list)
    for collection in data.COUNTRIES, data.COMMON_NAMES:
        for entry in collection.items():
            key = entry[0]
            value =  entry[1].__dict__['_proxy____args'][0]
            tmp[key].append(value)

    returns = list()
    for key in tmp:
        _ = [data.ALT_CODES[key][1], key, data.ALT_CODES[key][0]]
        _.append(True)
        _ += tmp[key][::-1] # Reverse the Country labels

        returns.append(_)
    returns.sort()
    returns += ADDITIONS
    return returns

    