import copy
import functools
from urllib import parse

import yaml


def make_cacher():
    cache = {}

    def kwargs_cacher(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if not cache:
                cache.update(kwargs)

            return f(*args, **cache)

        return wrapper

    return kwargs_cacher


kwargs_cacher = make_cacher()


def mutate_config_urls(config):
    result = copy.deepcopy(config)
    oa = result.get('oa', {})
    result['oa'] = oa

    oa_url = parse.urlparse(oa.get('openapi', {}).get('host', '//localhost'))

    oa['openapi'] = {
        'host': oa_url.hostname,
        'ssl': oa_url.scheme == 'https',
        'user': oa_url.username,
        'password': oa_url.password,
    }
    oa['openapi_url'] = parse.urlunparse(oa_url)

    if oa_url.port:
        oa['openapi']['port'] = oa_url.port

    return result


def config_dict(filename):
    with open(filename) as config:
        c = yaml.load(config)

    return c


@kwargs_cacher
def get_config(filename='config.yml'):
    return mutate_config_urls(config_dict(filename))
