"""
Interface to the adsws libraries api.
"""

import warnings
import six
import math
from werkzeug.utils import cached_property
import json

from .config import LIBRARIES_URL
from .exceptions import SolrResponseParseError, APIResponseError
from .base import BaseQuery, APIResponse
from .metrics import MetricsQuery
from .export import ExportQuery


class LibraryResponse(APIResponse):
    """
    Data structure that represents a response from the ads library service
    """
    def __init__(self, raw):
        self._raw = raw
        self.library = json.loads(raw)

    def __str__(self):
        if six.PY3:
            return self.__unicode__()
        return self.__unicode__().encode("utf-8")

    def __unicode__(self):
        return self.library



class LibraryQuery(BaseQuery):
    """
    Represents a query to the adsws libraries service
    """

    HTTP_ENDPOINT = LIBRARIES_URL

    def __init__(self, **kwargs):
        """
        :param library_name: The name of the private library to return.
        :type library_name: string
        """
        self.response = None  # current LibrariesResponse object
        #self.name = library_name
        self.json_payload = json.dumps({} or kwargs)

    def execute(self):
        """
        Execute the http request to the metrics service
        """
        self.response = self.session.get(self.HTTP_ENDPOINT + "libraries", data=self.json_payload)
        raise a
        return self.response.library




class Library(object):
    """
    An object to represent a single record in NASA's Astrophysical
    Data System.
    """
    def __init__(self, name, description=None, public=False, articles=None,
        **kwargs):
        """
        :param kwargs: Set object attributes from kwargs
        """
        return None

    #num_users,owner,public,permission,date_last_modified,date_created
    #num_documents,description,id,name,permissions,

    # def transfer



"""
Some use-cases:

lib = ads.Library("something", articles=[article1, article2, article3])

lib2 = ads.libraries.LibraryQuery("name")

# On-demand updates.
lib += article4
lib -= article2

"""


