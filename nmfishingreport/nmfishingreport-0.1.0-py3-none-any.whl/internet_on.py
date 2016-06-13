"""internet_on.py

Checks to make sure that an internet connection is present before
the rest of a script will run.
"""

import urllib.request
import time


class NoInternetError(Exception):
    '''Error for no internet connectivity.'''
    pass


def internet_on(retries=6, delay=5, timeout=1):
    google_url = 'http://google.com'

    for x in range(retries):
        try:
            with urllib.request.urlopen(google_url, timeout=timeout) as resp:
                return resp.status == 200
        except urllib.error.URLError:
            time.sleep(delay)
    raise NoInternetError('There was no internet connectivity when I tried to'
                          ' run at {}.'.format(time.asctime()))
