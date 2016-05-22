import ssl
import locale

from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager

_api_key = None
_preferred_language = (locale.getdefaultlocale()[0] or 'en-US').replace('_', '-')

BASE_URL = "https://api.sermonaudio.com/v1/"


def set_api_key(key: str):
    """Sets the SermonAudio API key to use for authenticated requests. A key must be set before making any requests.

    :param key: Your API key. Broadcasters may obtain an API key by going to the Member's Only area of the site. If you
    are an application developer and would like to integrate SermonAudio into your product or website, please contact
    us at info@sermonaudio.com and we'll be happy to discuss with you.
    """
    global _api_key
    _api_key = key


def set_preferred_language(http_accept_language: str):
    """Sets the preferred language string globally. Defaults to your system locale environment variables.

    The format of the string should be an acceptable HTTP Accept-Language header. You may specify multiple languages,
    and the API will attempt to accommodate your preferences when possible. While content language will always be
    determined by the broadcasters individually, other strings, whenever possible, will be translated."""
    global _preferred_language
    _preferred_language = http_accept_language


def get_request_headers(preferred_language_override=None, show_content_in_any_language=True):
    result = {
        'X-API-Key': _api_key,
        'Accept-Language': preferred_language_override or _preferred_language
    }

    if show_content_in_any_language:
        result['X-Show-All-Languages'] = True

    return result


class SecureRequestAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1_2)


# Require TLSv1.2 for all connections to the server
s = Session()
s.mount(BASE_URL, SecureRequestAdapter())
