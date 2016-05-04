# -*- coding: utf-8 -*-
import json
import logging
import requests
from zope.interface import Interface, implementer
from oe_utils.data.data_transfer_objects import ResultDTO

log = logging.getLogger(__name__)


def load_searchquery_parameters(query_params, user_acls=None):
    """
    Creates a query for the searchengine based on the provided params.

    :param params: the request params for the search action
    :param user_acls: an acces list for role based filtering
    :returns: Een :class:`dict` query object for the searchengine
    """
    q = {
        'match_all': {}
    }
    return q


def default_mapper(result, settings):
    if "hits" in result:
        result = [r['_source'] for r in result["hits"]["hits"]]
        return result
    else:
        return []


class ISearchEngine(Interface):
    def add_to_index(system_token, object_type, object_id, object_data):
        '''add an object to the index with a specific type'''

    def remove_from_index(system_token, object_type, object_id):
        '''remove an object from the index'''

    def query(system_token, object_type=None, query=None, sort='', options=None):
        '''execute a query on the search engine'''

    def remove_index(system_token):
        '''remove the index'''

    def create_index(system_token, data=None):
        '''create the index'''

    def add_type_mapping(object_type, object_type_mapping, system_token):
        '''add the mapping for specific type'''


@implementer(ISearchEngine)
class SearchEngine(object):
    def __init__(self, baseurl, index_name, default_type):
        self.baseurl = baseurl
        self.index_name = index_name
        self.default_type = default_type

    def add_to_index(self, system_token, object_type, object_id, object_data):
        '''add an object to the index with a specific type'''
        headers = {}
        if system_token:
            headers = {'OpenAmSSOID': system_token}
        res = requests.put(self.baseurl + '/' + self.index_name + '/' + object_type + '/' + str(object_id),
                           object_data, headers=headers)
        res.raise_for_status()

    def remove_from_index(self, system_token, object_type, object_id):
        '''remove an object from the index'''
        headers = {}
        if system_token:
            headers = {'OpenAmSSOID': system_token}
        res = requests.delete(self.baseurl + '/' + self.index_name + '/' + object_type + '/' + str(object_id),
                              headers=headers)
        res.raise_for_status()

    def query(self, system_token, object_type=None, query_params=None, sort=None, result_range=None,
              mapper=default_mapper, load_searchquery_param_func=load_searchquery_parameters,
              aggregations=None, settings=None, user_acls=None, min_score=None):
        '''execute a query on the search engine'''
        if object_type is None:
            object_type = self.default_type
        query = load_searchquery_param_func(query_params, user_acls)
        if not sort:
            sort = ['_score']
        params = {}
        if result_range:
            params['size'] = result_range.get_page_size()
            params['from'] = result_range.start
        data = {
            "query": query,
            "sort": sort,
        }
        if min_score:
            data["min_score"] = min_score
        if aggregations:
            data["aggregations"] = aggregations
        headers = {}
        if system_token:
            headers = {'OpenAmSSOID': system_token}
        res = requests.post(self.baseurl + "/" + self.index_name + '/' + object_type + '/_search',
                            data=json.dumps(data), params=params, headers=headers)
        res.raise_for_status()
        result = json.loads(res.text)
        return ResultDTO(mapper(result, settings), result["hits"]["total"] if "hits" in result else 0,
                         result["aggregations"] if "aggregations" in result else None)

    def remove_index(self, system_token):
        headers = {}
        if system_token:
            headers = {'OpenAmSSOID': system_token}
        res = requests.head(self.baseurl + "/" + self.index_name, headers=headers)
        if res.status_code < 400:  # otherwise assume index doens't exists
            res = requests.delete(self.baseurl + "/" + self.index_name, headers=headers)
            res.raise_for_status()

    def create_index(self, system_token, data):
        headers = {}
        if system_token:
            headers = {'OpenAmSSOID': system_token}
        res = requests.put(self.baseurl + "/" + self.index_name, data=json.dumps(data), headers=headers)
        res.raise_for_status()

    def add_type_mapping(self, object_type, object_type_mapping, system_token):
        headers = {}
        if system_token:
            headers = {'OpenAmSSOID': system_token}
        res = requests.put(self.baseurl + "/" + self.index_name + '/_mapping/' + object_type,
                           data=json.dumps(object_type_mapping), headers=headers)
        res.raise_for_status()
