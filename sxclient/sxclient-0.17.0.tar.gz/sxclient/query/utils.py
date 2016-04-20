'''
Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: Apache 2.0, see LICENSE for more details.
'''
from sxclient.models import QueryParameters


def job_poll_params(req_id):
    '''Create query parameters object for job poll query.'''
    params = QueryParameters(
        sx_verb='GET',
        path_items=['.results', req_id],
        bool_params=set(),
        dict_params={},
    )
    return params
