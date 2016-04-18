import urllib

import requests
from flarecast.utils.rest_exception import RestException


class PropertyDBClient(object):
    __ADD_PROPERTY = '/property/%s'
    __ADD_PROPERTY_BY_PROVENANCE = '/property/%s/%s'

    __INSERT_PROPERTIES = '/property/bulk'
    __INSERT_PROPERTIES_BY_PROVENANCE = '/property/%s/bulk'

    __ADD_PROVENANCE = '/provenance'
    __INSERT_PROVENANCE = '/provenance/bulk'
    __GET_PROVENANCE = '/provenance/%s'
    __GET_PROVENANCES = '/provenance/list'

    __ADD_REGION = '/region/%s'
    __INSERT_REGIONS = '/region/%s/bulk'
    __DELETE_REGIONS = '/region/%s/bulk%s'

    __QUERY_PROPERTIES = '/property/%s/list%s'
    __QUERY_PROPERTIES_BY_OBS_DATE = '/property/%s/%s/list%s'
    __QUERY_PROPERTIES_EVOLUTION = '/property/%s/%s/%s/list%s'

    __INSERT_LINK_URL = '/link/bulk'
    __QUERY_LINKS_BY_TIME_RANGE = '/link/%s/%s/%s/list%s'
    __QUERY_LINKS_BY_FC_ID = '/link/%s/%s/list'
    __QUERY_LINK_GRAPH = '/link/%s/%s/graph'

    def __init__(self, property_db_url):
        self.property_db_url = property_db_url

    # -- delete --

    def delete_regions(self, provenance, sirql_arguments=''):
        if sirql_arguments != '':
            sirql_arguments = '?' + sirql_arguments

        url = self.property_db_url + self.__DELETE_REGIONS % (
            provenance,
            sirql_arguments)
        return self.__delete_request(url)

    # -- inserts --

    def insert_regions(self, provenance, property_groups):
        url = self.property_db_url + self.__INSERT_REGIONS % (
            provenance)
        return self.__post_request(url, property_groups)

    def insert_properties(self, properties):
        url = self.property_db_url + self.__INSERT_PROPERTIES
        return self.__post_request(url, properties)

    # todo: name this properly
    def insert_properties_as_provenance(self, provenance, properties):
        url = self.property_db_url + \
              self.__INSERT_PROPERTIES_BY_PROVENANCE % \
              provenance
        return self.__post_request(url, properties)

    def insert_provenances(self, provenance_list):
        url = self.property_db_url + self.__INSERT_PROVENANCE
        return self.__post_request(url, provenance_list)

    def insert_links(self, link_list):
        url = self.property_db_url + self.__INSERT_LINK_URL
        return self.__post_request(url, link_list)

    # -- add --

    def add_provenance(self, name):
        url = self.property_db_url + self.__ADD_PROVENANCE
        return self.__post_request(url, name)

    def add_region(self, provenance, time_start, **attributes):
        group = {'time_start': time_start}
        group.update(attributes)

        url = self.property_db_url + self.__ADD_REGION % provenance
        return self.__post_request(url, group)

    def add_properties(self, region_fc_id, provenance=None,
                       **properties):
        props = {region_fc_id: properties}

        if provenance is None:
            return self.insert_properties(props)

        url = self.property_db_url + self.__ADD_PROPERTY_BY_PROVENANCE % (
            provenance, urllib.quote(region_fc_id, safe=''))
        return self.__post_request(url, properties)

    def add_link(self, source, target, link_type, description=''):
        link = {'source': source,
                'target': target,
                'type': link_type,
                'description': description}
        return self.insert_links([link])

    # -- get --

    def get_properties(self, provenance, sirql_arguments=''):
        if sirql_arguments != '':
            sirql_arguments = '?' + sirql_arguments

        url = self.property_db_url + self.__QUERY_PROPERTIES % (
            provenance,
            sirql_arguments)

        return self.__get_request(url)

    def get_properties_by_obs_date(self, provenance, obs_date,
                                   sirql_arguments=''):
        if sirql_arguments != '':
            sirql_arguments = '?' + sirql_arguments

        query_str = self.__QUERY_PROPERTIES_BY_OBS_DATE % (
            provenance, obs_date, sirql_arguments
        )
        url = self.property_db_url + query_str
        return self.__get_request(url)

    def get_properties_by_time_range(self,
                                     provenance,
                                     from_date,
                                     to_date,
                                     sirql_arguments=''):

        # add time-range query
        range_query = 'time_start=between("%s", "%s")' % (from_date, to_date)
        sirql_arguments = '&'.join([sirql_arguments, range_query])

        if sirql_arguments != '':
            sirql_arguments = '?' + sirql_arguments

        query_str = self.__QUERY_PROPERTIES % (
            provenance, sirql_arguments
        )
        url = self.property_db_url + query_str
        return self.__get_request(url)

    def get_property_evolution(self,
                               provenance,
                               from_date,
                               to_date,
                               property_name,
                               sirql_arguments=''):
        if sirql_arguments != '':
            sirql_arguments = '?' + sirql_arguments

        # add query

        query_str = self.__QUERY_PROPERTIES_EVOLUTION % (
            provenance, from_date, to_date, sirql_arguments
        )
        url = self.property_db_url + query_str
        return self.__get_request(url)

    def get_provenance(self, provenance):
        url = self.property_db_url + self.__GET_PROVENANCE % provenance
        return self.__get_request(url)

    def get_provenances(self):
        url = self.property_db_url + self.__GET_PROVENANCES
        return self.__get_request(url)

    def get_links_by_time_range(self, link_type, from_date, to_date,
                                sirql_arguments=''):
        if sirql_arguments != '':
            sirql_arguments = '?' + sirql_arguments
        query_str = self.__QUERY_LINKS_BY_TIME_RANGE % (
            link_type, from_date, to_date, sirql_arguments
        )
        url = self.property_db_url + query_str
        return self.__get_request(url)

    def get_links(self, fc_id, link_type):
        url = self.property_db_url + self.__QUERY_LINKS_BY_FC_ID % (
            fc_id, link_type)
        return self.__get_request(url)

    def get_link_graph(self, fc_id, link_type):
        url = self.property_db_url + self.__QUERY_LINK_GRAPH % (
            fc_id, link_type)
        return self.__get_request(url)

    @staticmethod
    def __post_request(url, payload):
        headers = {'Content-Type': 'application/json'}
        r = requests.post(url, json=payload, headers=headers)

        if r.status_code != 200:
            raise RestException(r)

        return r.json()

    @staticmethod
    def __delete_request(url):
        r = requests.delete(url)

        if r.status_code != 200:
            raise RestException(r)

        return r.text

    @staticmethod
    def __get_request(url):
        r = requests.get(url)

        if r.status_code != 200:
            raise RestException(r)

        return r.json()
