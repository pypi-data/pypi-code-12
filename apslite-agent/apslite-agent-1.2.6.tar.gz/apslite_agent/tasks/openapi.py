import logging
from pydoc import locate
from functools import reduce

from osaapi import OSA, Transaction
import requests

from apslite_agent.config import get_config
from apslite_agent.tasks import base

logger = logging.getLogger(__name__)


def mgetattr(obj, attr):
    return reduce(getattr, [obj] + attr.split('.'))


class OpenAPI(base.Task):
    name = 'openapi'

    def __init__(self, openapi, rest_url):
        self.openapi = openapi
        self.results = {}
        self.rest_url = rest_url

    def remove_old_oauth(self, url, headers, key, **kwargs):
        url = '{}{}'.format(self.rest_url, url)

        try:
            res = requests.get(url=url, headers=headers, verify=False)
            instances = res.json()
        except Exception as e:
            logger.error("Remove old oauth error: %s", e)
            return {'error': 'remove_old_oauth',
                    'message': 'Remove old oauth error: {}'.format(e)}

        for instance in instances:
            if 'oauth' in instance.get('aps', {}).get('auth', {})\
                    and instance['aps']['auth']['oauth'].get('key', '') == key:
                try:
                    ret = requests.request(
                        url='{}{}'.format(url, instance['aps']['id']),
                        headers=headers,
                        timeout=20,
                        **kwargs
                    )
                    if ret.status_code != 204:
                        raise Exception(ret.content)
                except Exception as e:
                    logger.error("Remove old oauth error: %s", e)
                    return {'error': 'remove_old_oauth',
                            'message': 'Remove old oauth error: {}'.format(e)}
        return {}

    def set_oauth(self, url, headers, **kwargs):
        url = '{}{}'.format(self.rest_url, url)

        try:
            res = requests.get(url=url, headers=headers, verify=False)
            instances = res.json()
            resource_id = self.results['app_instance']['application_resource_id']
        except Exception as e:
            logger.error("Remove old oauth error: %s", e)
            return {'error': 'remove_old_oauth',
                    'message': 'Remove old oauth error: {}'.format(e)}

        for instance in instances:
            if instance.get('app', {}).get('aps', {}).get('id', '') == resource_id:
                try:
                    ret = requests.request(
                        url='{}{}'.format(url, instance['aps']['id']),
                        headers=headers,
                        timeout=20,
                        **kwargs
                    )
                    if ret.status_code != 204:
                        raise Exception(ret.content)
                except Exception as e:
                    logger.error("Set oauth error: %s", e)
                    return {'error': 'oauth_error',
                            'message': 'Set oauth error: {}'.format(e)}
        return {}

    def run(self):
        self.results = self.data['results'] if 'results' in self.data else {}

        if not self.openapi:
            return self.result('Error', "Improperly configured")

        try:
            methods = self.data['methods']
        except IndexError:
            return self.result('Error', "Missing required parameter: 'methods'")

        p = OSA(**self.openapi)

        for method in methods:
            try:
                args = self.get_args(method.get('args', {}))

                logger.info("Calling OpenAPI method '%s' with arguments: %s",
                            method.get('name'),
                            args)

                if 'type' not in method or ('type' in method and method['type'] == 'openapi'):
                    def run():
                        return mgetattr(p, method['name'])(**args)

                    if method.get('transaction', True):
                        with Transaction(p):
                            ret = run()
                    else:
                        ret = run()

                elif method['type'] == 'rest':
                    # args.url for substituting parameters
                    args['url'] = '{}{}{}'.format(
                        self.rest_url, method['name'], args.get('url', '')
                    )
                    ret = requests.request(**args).json()
                    logger.info('REST Api data: %s', ret)
                elif method['type'] == 'workaround' and hasattr(self, method['name']):
                    # workaround logic
                    ret = getattr(self, method['name'])(**args)

                if 'error' in ret or ('status' in ret and ret['status'] != 0):
                    error_message = ret['message'] if 'message' in ret else 'Error'
                    raise Exception(ret.get('error_message', error_message))

                result = ret.get('result', ret)

                self.results[method.get('id', '')] = result
                self.results['_'] = result
            except Exception as e:
                self.data['results'] = self.results
                return self.result('Error', str(e), self.data)

        self.results.pop('_')
        self.data['results'] = self.results

        return self.result('OK', '', self.data)

    def get_args(self, method_args):
        """
        Iterate over existing results and supplied args, substituting @N:param_name
        with actual parameter value from Nth result.
        """

        args = {}

        for arg, value in method_args.items():
            if isinstance(value, list):
                new_value = []
                for item in value:
                    if isinstance(item, dict):
                        item = self.get_args(item)
                    new_value.append(item)
                args[arg] = new_value
            elif isinstance(value, dict):
                args[arg] = self.get_args(value)
            elif isinstance(value, str) and value.startswith('@'):
                try:
                    values = value[1:].split(':')
                    _type = None
                    if len(values) == 2:
                        rid, key = values
                    else:
                        rid, key, _type = values

                    args[arg] = reduce(lambda val, k: val[k],
                                       key.split('.'),
                                       self.results[rid])
                    if _type:
                        args[arg] = locate(_type)(args[arg])

                except Exception:
                    logger.warn("Skipping parameter that looks like a reference, but is badly "
                                "formatted: '%s'",
                                value)
                    args[arg] = value
            else:
                args[arg] = value

        return args


def task_factory(**kwargs):
    c = get_config()
    openapi = c.get('oa', {}).get('openapi', {})
    rest_url = c.get('oa', {}).get('rest_url', '')

    return {
        OpenAPI.name: OpenAPI(openapi, rest_url)
    }
