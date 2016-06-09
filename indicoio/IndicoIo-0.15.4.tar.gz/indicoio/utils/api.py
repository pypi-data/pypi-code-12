"""
Handles making requests to the IndicoApi Server
"""

import json
import requests
import warnings

try:
    from urllib import urlencode
except: # For Python 3
    from urllib.parse import urlencode

from indicoio.utils.errors import IndicoError
from indicoio import JSON_HEADERS
from indicoio import config

def api_handler(arg, cloud, api, url_params=None, **kwargs):
    """
    Sends finalized request data to ML server and receives response.
    """
    url_params = url_params or {}
    if type(arg) == bytes:
        arg = arg.decode('utf-8')
    if type(arg) == list:
        arg = [a.decode('utf-8') if type(arg) == bytes else a for a in arg]
   
    cloud = cloud or config.cloud
    host = "%s.indico.domains" % cloud if cloud else config.host

    # LOCAL DEPLOYMENTS
    if not (host.endswith('indico.domains') or host.endswith('indico.io')):
        url_protocol = "http"
    else:
        url_protocol = config.url_protocol

    headers = dict(JSON_HEADERS)
    headers["X-ApiKey"] = url_params.get("api_key") or config.api_key
    url = create_url(url_protocol, host, api, dict(kwargs, **url_params))

    data = {'data': arg}
    data.update(**kwargs)
    json_data = json.dumps(data)

    response = requests.post(url, data=json_data, headers=headers)

    warning = response.headers.get('x-warning')
    if warning:
        warnings.warn(warning)

    if response.status_code == 503 and cloud != None:
        raise IndicoError("Private cloud '%s' does not include api '%s'" % (cloud, api))

    json_results = response.json()
    results = json_results.get('results', False)
    if results is False:
        error = json_results.get('error')
        raise IndicoError(error)
    return results


def create_url(url_protocol, host, api, url_params):
    is_batch = url_params.pop("batch", None)
    apis = url_params.pop("apis", None)
    version = url_params.pop("version", None) or url_params.pop("v", None)
    method = url_params.pop('method', None)

    host_url_seg = url_protocol + "://%s" % host
    api_url_seg = "/%s" % api
    batch_url_seg = "/batch" if is_batch else ""
    method_url_seg = "/%s" % method if method else ""

    params = {}
    if apis:
        params["apis"] = ",".join(apis)
    if version:
        params["version"] = version

    url = host_url_seg + api_url_seg + batch_url_seg + method_url_seg
    if params:
        url += "?" + urlencode(params)

    return url
