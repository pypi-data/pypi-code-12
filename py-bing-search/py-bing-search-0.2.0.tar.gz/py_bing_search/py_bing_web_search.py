import urllib2
import requests
import pdb
import time

from py_bing_search import PyBingSearch

class PyBingWebException(Exception):
    pass

class PyBingWebSearch(PyBingSearch):

    IMAGE_QUERY_BASE = 'https://api.datamarket.azure.com/Bing/Search/Web' \
                 + '?Query={}&$top={}&$skip={}&$format={}'

    def __init__(self, api_key, query, safe=False):
        PyBingSearch.__init__(self, api_key, query, self.IMAGE_QUERY_BASE, safe=safe)
        #self.api_key = api_key
        #self.safe = safe
        #self.current_offset = 0
        #self.query = query

    def _search(self, limit, format):
        '''
        Returns a list of result objects, with the url for the next page bing search url.
        '''
        url = self.QUERY_URL.format(urllib2.quote("'{}'".format(self.query)), min(50, limit), self.current_offset, format)
        r = requests.get(url, auth=("", self.api_key))
        try:
            json_results = r.json()
        except ValueError as vE:
            if not self.safe:
                raise PyBingWebException("Request returned with code %s, error msg: %s" % (r.status_code, r.text))
            else:
                print "[ERROR] Request returned with code %s, error msg: %s. \nContinuing in 5 seconds." % (r.status_code, r.text)
                time.sleep(5)
        packaged_results = [WebResult(single_result_json) for single_result_json in json_results['d']['results']]
        self.current_offset += min(50, limit, len(packaged_results))
        return packaged_results

class WebResult(object):
    '''
    The class represents a SINGLE search result.
    Each result will come with the following:

    #For the actual results#
    title: title of the result
    url: the url of the result
    description: description for the result
    id: bing id for the page

    #Meta info#:
    meta.uri: the search uri for bing
    meta.type: for the most part WebResult
    '''

    class _Meta(object):
        '''
        Holds the meta info for the result.
        '''
        def __init__(self, meta):
            self.type = meta['type']
            self.uri = meta['uri']

    def __init__(self, result):
        self.url = result['Url']
        self.title = result['Title']
        self.description = result['Description']
        self.id = result['ID']

        self.meta = self._Meta(result['__metadata'])
