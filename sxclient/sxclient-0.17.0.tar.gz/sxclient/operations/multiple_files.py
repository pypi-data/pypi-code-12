'''
Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: Apache 2.0, see LICENSE for more details.
'''
from collections import OrderedDict

from sxclient.operations.base import VolumeNodeOperation
from sxclient.models.query_parameters import QueryParameters


__all__ = ['ListFiles']


class ListFiles(VolumeNodeOperation):
    '''
    List files in an SX volume.


    Required access: read access

    Query-specific parameters:
      - volume -- the name of the volume to list
      - filter -- an optional argument to limit the results returned
        to only those matching $pattern.
        The pattern may contain wildcard characters: ?, * and [.
        The escape character is: \\
      - recursive -- an optional parameter indicating whether the file list
        should recurse into subdirectories
      - limit -- an optional parameter to limit the number of returned results
        to a maximum of $maxobjs entries (used in conjunction with after
        to retrieve the list in smaller chunks)
      - after -- an optional parameter that indicates the starting position
        in the result set (used in conjunction with after to retrieve the list
        in smaller chunks)
    '''

    def json_call(self, *args, **kwargs):
        return self.call(*args, **kwargs).json(object_pairs_hook=OrderedDict)

    def _generate_query_params(
        self, volume, filter=None, recursive=None, limit=None, after=None
    ):
        bool_params = set()
        dict_params = {'o': 'list'}
        if recursive is not None:
            bool_params.add('recursive')
        if filter is not None:
            dict_params['filter'] = filter
        if limit is not None:
            dict_params['limit'] = limit
        if after is not None:
            dict_params['after'] = after

        return QueryParameters(
            sx_verb='GET',
            path_items=[volume],
            bool_params=bool_params,
            dict_params=dict_params
        )
