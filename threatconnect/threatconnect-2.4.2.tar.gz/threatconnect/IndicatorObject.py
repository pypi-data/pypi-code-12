""" standard """
import csv
import json
import urllib
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

""" custom """
import VictimObject
from AttributeObject import parse_attribute, AttributeObject
from FileOccurrenceObject import parse_file_occurrence
import GroupObject
from SecurityLabelObject import parse_security_label
from TagObject import parse_tag


import ApiProperties
from Config.ResourceType import ResourceType
from ErrorCodes import ErrorCodes

from RequestObject import RequestObject
from SharedMethods import get_resource_type, get_hash_type, get_resource_indicator_type


def parse_indicator(indicator_dict, resource_obj=None, api_filter=None, request_uri=None, indicators_regex=None):
    """ """
    # indicator object
    indicator = IndicatorObject()

    #
    # standard values
    #
    indicator.set_date_added(indicator_dict['dateAdded'])
    indicator.set_id(indicator_dict['id'])
    indicator.set_last_modified(indicator_dict['lastModified'])
    indicator.set_weblink(indicator_dict['webLink'])

    #
    # optional values
    #
    if 'type' in indicator_dict:
        indicator.set_type(indicator_dict['type'])  # set type before indicator

    if 'confidence' in indicator_dict:
        indicator.set_confidence(indicator_dict['confidence'], update=False)
    if 'description' in indicator_dict:
        indicator.set_description(indicator_dict['description'], update=False)
    if 'owner' in indicator_dict:  # nested owner for single indicator result
        indicator.set_owner_name(indicator_dict['owner']['name'])
    if 'ownerName' in indicator_dict:
        indicator.set_owner_name(indicator_dict['ownerName'])
    if 'rating' in indicator_dict:
        indicator.set_rating(indicator_dict['rating'], update=False)
    if 'summary' in indicator_dict:
        resource_type = get_resource_type(indicators_regex, indicator_dict['summary'])
        indicator.set_indicator(indicator_dict['summary'], resource_type)
    if 'threatAssessConfidence' in indicator_dict:
        indicator.set_threat_assess_confidence(indicator_dict['threatAssessConfidence'])
    if 'threatAssessRating' in indicator_dict:
        indicator.set_threat_assess_rating(indicator_dict['threatAssessRating'])

    #
    # address
    #
    if 'ip' in indicator_dict:
        indicator.set_indicator(indicator_dict['ip'], ResourceType.ADDRESSES)
        if indicator.type is None:
            indicator.set_type('Address')  # set type before indicator

    #
    # email address
    #
    if 'address' in indicator_dict:
        indicator.set_indicator(indicator_dict['address'], ResourceType.EMAIL_ADDRESSES)
        if indicator.type is None:
            indicator.set_type('EmailAddress')  # set type before indicator

    #
    # files
    #
    if 'md5' in indicator_dict:
        indicator.set_indicator(indicator_dict['md5'], ResourceType.FILES)
        if indicator.type is None:
            indicator.set_type('File')  # set type before indicator

    if 'sha1' in indicator_dict:
        indicator.set_indicator(indicator_dict['sha1'], ResourceType.FILES)
        if indicator.type is None:
            indicator.set_type('File')  # set type before indicator

    if 'sha256' in indicator_dict:
        indicator.set_indicator(indicator_dict['sha256'], ResourceType.FILES)
        if indicator.type is None:
            indicator.set_type('File')  # set type before indicator

    if 'size' in indicator_dict:
        indicator.set_size(indicator_dict['size'], update=False)

    #
    # hosts
    #
    if 'hostName' in indicator_dict:
        indicator.set_indicator(indicator_dict['hostName'], ResourceType.HOSTS)
        if indicator.type is None:
            indicator.set_type('Host')  # set type before indicator

    if 'dnsActive' in indicator_dict:
        indicator.set_dns_active(indicator_dict['dnsActive'], update=False)

    if 'whoisActive' in indicator_dict:
        indicator.set_whois_active(indicator_dict['whoisActive'], update=False)

    #
    # urls
    #
    if 'text' in indicator_dict:
        indicator.set_indicator(indicator_dict['text'], ResourceType.URLS)
        if indicator.type is None:
            indicator.set_type('URL')  # set type before indicator

    if 'source' in indicator_dict:
        indicator.set_source(indicator_dict['source'], update=False)

    #
    # attributes
    #
    if 'attribute' in indicator_dict:
        for attribute_dict in indicator_dict['attribute']:
            attribute = parse_attribute(attribute_dict, indicator)
            indicator.add_attribute(attribute)

    #
    # tag
    #
    if 'tag' in indicator_dict:
        for tag_dict in indicator_dict['tag']:
            tag = parse_tag(tag_dict)
            indicator.add_tag(tag)

    #
    # handle both resource containers and individual objects
    #
    if resource_obj is not None:
        # store the resource object in the master resource object list
        # must be submitted after parameters are set for indexing to work
        roi = resource_obj.add_master_resource_obj(indicator, indicator_dict['id'])

        # BCS - This causes a bug on searching for a single indicator over multiple
        #       owners, only 1 indicator is returned.
        # roi = resource_obj.add_master_resource_obj(indicator, indicator.indicator)

        # retrieve the resource object and update data
        return resource_obj.get_resource_by_identity(roi)

    #
    # filter (set after retrieving stored object)
    #
    if api_filter is not None:
        indicator.add_matched_filter(api_filter)

    #
    # request_uri (set after retrieving stored object)
    #
    if request_uri is not None:
        indicator.add_request_uri(request_uri)

    return indicator


class IndicatorObject(object):
    __slots__ = (
        '_address',  # email address specific indicator
        '_attributes',
        '_confidence',
        '_date_added',
        '_description',
        '_dns_active',  # host indicator type specific
        '_dns_resolutions',  # host indicator type specific
        '_file_occurrences',  # file indicator type specific
        '_hostname',  # host specific indicator
        '_id',
        '_ip',  # address specific indicator
        '_size',  # file indicator type specific
        '_last_modified',
        '_matched_filters',
        '_md5',  # file specific indicator
        '_owner_name',
        '_phase',  # 0 - new; 1 - add; 2 - update
        '_properties',
        '_rating',
        '_reference_indicator',
        '_request_uris',
        '_resource_type',
        '_security_label',
        '_sha1',  # file specific indicator
        '_sha256',  # file specific indicator
        '_source',  # url indicator type specific
        '_tags',
        '_text',  # url specific indicator
        '_threat_assess_confidence',
        '_threat_assess_rating',
        '_type',
        '_weblink',
        '_whois_active',  # host indicator type specific
        '_reload_attributes',
    )

    def __init__(self, resource_type_enum=None):
        self._attributes = []
        self._address = None  # email indicator type specific
        self._confidence = None
        self._date_added = None
        self._description = None
        self._dns_active = None  # host indicator type specific
        self._dns_resolutions = []  # host indicator type specific
        self._file_occurrences = []  # file indicator type specific
        self._size = None  # file indicator type specific
        # self._groups = []
        self._id = None
        self._hostname = None  # host indicator type specific
        self._ip = None  # address indicator type specific
        self._last_modified = None
        self._matched_filters = []
        self._md5 = None  # file indicator type specific
        self._owner_name = None
        self._phase = 0
        self._reload_attributes = False
        self._properties = {
            '_confidence': {
                'api_field': 'confidence',
                'method': 'set_confidence',
                'required': False,
            },
            '_rating': {
                'api_field': 'rating',
                'method': 'set_rating',
                'required': False,
            }
        }
        self._rating = None
        self._reference_indicator = None
        self._request_uris = []
        self._resource_type = resource_type_enum
        self._security_label = None
        self._sha1 = None  # file indicator type specific
        self._sha256 = None  # file indicator type specific
        self._source = None  # url indicator type specific
        self._tags = []
        self._text = None  # url indicator type specific
        self._threat_assess_confidence = None
        self._threat_assess_rating = None
        self._type = None
        self._weblink = None
        self._whois_active = None  # host indicator type specific

    #
    # unicode
    #
    @staticmethod
    def _uni(data):
        """ """
        if data is None or isinstance(data, (int, list, dict)):
            return data
        elif isinstance(data, unicode):
            return unicode(data.encode('utf-8').strip(), errors='ignore')  # re-encode poorly encoded unicode
        elif not isinstance(data, unicode):
            return unicode(data, 'utf-8', errors='ignore')
        else:
            return data

    #
    # urlsafe
    #
    @staticmethod
    def _urlsafe(data):
        """ url encode value for safe request """
        return urllib.quote(data, safe='~')

    """ shared indicator methods """

    #
    # confidence
    #

    @property
    def confidence(self):
        """ """
        return self._confidence

    def set_confidence(self, data, update=True):
        """Read-Write indicator metadata"""
        if isinstance(data, int):
            if 0 <= data <= 100:
                self._confidence = data
            else:
                raise AttributeError(ErrorCodes.e10010.value.format(data))
        else:
            raise AttributeError(ErrorCodes.e10011.value.format(data))

        if update and self._phase == 0:
            self._phase = 2

    #
    # date_added
    #
    @property
    def date_added(self):
        """ """
        return self._date_added

    def set_date_added(self, data):
        """Read-Only indicator metadata"""
        self._date_added = data

    #
    # description
    #
    @property
    def description(self):
        """ """
        return self._description

    def set_description(self, data, update=True):
        """Read-Write indicator metadata"""
        self._description = self._uni(data)

        if update and self._phase == 0:
            self._phase = 2

    #
    # dns_active (host indicator type specific)
    #
    @property
    def dns_active(self):
        """ """
        if self._resource_type == ResourceType.HOSTS:
            return self._dns_active
        else:
            raise AttributeError(ErrorCodes.e10100.value)

    def set_dns_active(self, data, update=True):
        """ """
        if self._resource_type == ResourceType.HOSTS:
            self._dns_active = self._uni(data)
        else:
            raise AttributeError(ErrorCodes.e10100.value)

        if update and self._phase == 0:
            self._phase = 2

    #
    # dns resolutions (host indicator type specific)
    #
    @property
    def dns_resolutions(self):
        """ """
        if self._resource_type == ResourceType.HOSTS:
            return self._dns_resolutions
        else:
            raise AttributeError(ErrorCodes.e10110.value)

    def add_dns_resolution(self, data_obj):
        """Read-Only indicator metadata"""
        if self._resource_type == ResourceType.HOSTS:
            if isinstance(data_obj, list):
                self._dns_resolutions.extend(data_obj)
            else:
                self._dns_resolutions.append(data_obj)

        else:
            raise AttributeError(ErrorCodes.e10110.value)

    #
    # file_occurrences (file indicator type specific)
    #
    @property
    def file_occurrences(self):
        """ """
        if self._resource_type == ResourceType.FILES:
            return self._file_occurrences
        else:
            raise AttributeError(ErrorCodes.e10120.value)

    def add_file_occurrence(self, data_obj):
        """Read-Only indicator metadata"""
        if self._resource_type == ResourceType.FILES:
            self._file_occurrences.append(data_obj)
        else:
            raise AttributeError(ErrorCodes.e10120.value)

    #
    # id
    #
    @property
    def id(self):
        """ """
        return self._id

    def set_id(self, data):
        """Read-Only indicator metadata"""
        if isinstance(data, (int, long)):
            self._id = data
        else:
            raise AttributeError(ErrorCodes.e10020.value.format(data))

    #
    # indicator
    #
    @property
    def indicator(self):
        """ """
        if self._resource_type == ResourceType.ADDRESSES:
            return self._ip
        elif self._resource_type == ResourceType.EMAIL_ADDRESSES:
            return self._address
        elif self._resource_type == ResourceType.FILES:
            return {
                'md5': self._md5,
                'sha1': self._sha1,
                'sha256': self._sha256,
            }
        elif self._resource_type == ResourceType.HOSTS:
            return self._hostname
        elif self._resource_type == ResourceType.URLS:
            return self._text
        else:
            raise AttributeError(ErrorCodes.e10030.value)

    def set_indicator(self, data, resource_type=None, update=True):
        """Read-Write indicator metadata"""
        if self._resource_type is None:
            if resource_type is None:
                # get resource type using regex
                self._resource_type = get_resource_type(self._tc._indicators_regex, data)
            else:
                self._resource_type = resource_type

        # if get_resource_type return None error.
        if not isinstance(self._resource_type, ResourceType):
            raise AttributeError(ErrorCodes.e10030.value)

        #
        # address
        #
        if self._resource_type == ResourceType.ADDRESSES:
            self._ip = self._uni(data)
            self._reference_indicator = self._urlsafe(self._ip)

            # additional resource type specific attributes
            self._properties['_ip'] = {
                'api_field': 'ip',
                'method': 'set_indicator',
                'required': True,
            }

        #
        # email_address
        #
        if self._resource_type == ResourceType.EMAIL_ADDRESSES:
            self._address = self._uni(data)
            self._reference_indicator = self._urlsafe(self._address)

            # additional resource type specific attributes
            self._properties['_address'] = {
                'api_field': 'address',
                'method': 'set_indicator',
                'required': True,
            }

        #
        # files
        #
        if self._resource_type == ResourceType.FILES:
            # handle different hash type
            hash_type = get_hash_type(data)
            if hash_type == 'MD5':
                self._md5 = data
                if self._reference_indicator is None:  # reference indicator for attr, tag, etc adds
                    self._reference_indicator = self._urlsafe(self._md5)
            elif hash_type == 'SHA1':
                self._sha1 = data
                if self._reference_indicator is None:  # reference indicator for attr, tag, etc adds
                    self._reference_indicator = self._urlsafe(self._sha1)
            elif hash_type == 'SHA256':
                self._sha256 = data
                if self._reference_indicator is None:  # reference indicator for attr, tag, etc adds
                    self._reference_indicator = self._urlsafe(self._sha256)

            self._properties['_md5'] = {
                'api_field': 'md5',
                'method': 'set_indicator',
                'required': True,
            }
            self._properties['_sha1'] = {
                'api_field': 'sha1',
                'method': 'set_indicator',
                'required': True,
            }
            self._properties['_sha256'] = {
                'api_field': 'sha256',
                'method': 'set_indicator',
                'required': True,
            }
            self._properties['_size'] = {
                'api_field': 'size',
                'method': 'set_size',
                'required': False,
            }

            if update and self._phase == 0:
                self._phase = 2

        #
        # hosts
        #
        if self._resource_type == ResourceType.HOSTS:
            self._hostname = self._uni(data)
            self._reference_indicator = self._urlsafe(self._hostname)

            # additional resource type specific attributes
            self._properties['_hostname'] = {
                'api_field': 'hostName',
                'method': 'set_indicator',
                'required': True,
            }
            self._properties['_dns_active'] = {
                'api_field': 'dnsActive',
                'method': 'set_dns_active',
                'required': False,
            }
            self._properties['_whois_active'] = {
                'api_field': 'whoisActive',
                'method': 'set_whois_active',
                'required': False,
            }

        #
        # urls
        #
        if self._resource_type == ResourceType.URLS:
            self._text = self._uni(data)
            self._reference_indicator = self._urlsafe(self._text)

            # additional resource type specific attributes
            self._properties['_text'] = {
                'api_field': 'text',
                'method': 'set_indicator',
                'required': True,
            }

    #
    # last_modified
    #
    @property
    def last_modified(self):
        """ """
        return self._last_modified

    def set_last_modified(self, data):
        """Read-Only indicator metadata"""
        self._last_modified = data

    #
    # owner_name
    #
    @property
    def owner_name(self):
        """ """
        return self._owner_name

    def set_owner_name(self, data):
        """Read-Only indicator metadata"""
        self._owner_name = self._uni(data)

    #
    # matched filters
    #
    @property
    def matched_filters(self):
        """ """
        return self._matched_filters

    def add_matched_filter(self, data):
        """ """
        if data not in self._matched_filters and data is not None:
            self._matched_filters.append(data)

    #
    # rating
    #
    @property
    def rating(self):
        """ """
        return self._rating

    def set_rating(self, data, update=True):
        """Read-Write indicator metadata"""
        self._rating = data

        # determine if POST or PUT
        if update and self._phase == 0:
            self._phase = 2

    #
    # size (file indicator type specific)
    #
    @property
    def size(self):
        """ """
        if self._resource_type == ResourceType.FILES:
            return self._size
        else:
            raise AttributeError(ErrorCodes.e10130.value)

    def set_size(self, data, update=True):
        """ """
        if self._resource_type == ResourceType.FILES:
            self._size = self._uni(str(data))
        else:
            raise AttributeError(ErrorCodes.e10130.value)

        if update and self._phase == 0:
            self._phase = 2

    #
    # source (url indicator type specific)
    #
    @property
    def source(self):
        """ """
        return self._source

    def set_source(self, data, update=True):
        """ """
        self._source = self._uni(data)

        if update and self._phase == 0:
            self._phase = 2

    #
    # threat assesses confidence
    #
    @property
    def threat_assess_confidence(self):
        """ """
        return self._threat_assess_confidence

    def set_threat_assess_confidence(self, data):
        """Read-Only indicator metadata"""
        self._threat_assess_confidence = data

    #
    # threat assesses rating
    #
    @property
    def threat_assess_rating(self):
        """ """
        return self._threat_assess_rating

    def set_threat_assess_rating(self, data):
        """Read-Only indicator metadata"""
        self._threat_assess_rating = data

    #
    # type
    #
    @property
    def type(self):
        """ """
        return self._type

    def set_type(self, data):
        """ """
        self._type = self._uni(data)
        self._resource_type = get_resource_indicator_type(self._type)

    #
    # weblink
    #
    @property
    def weblink(self):
        """ """
        return self._weblink

    def set_weblink(self, data):
        """ """
        self._weblink = self._uni(data)

    #
    # whois_active (host indicator type specific)
    #
    @property
    def whois_active(self):
        """ """
        if self._resource_type == ResourceType.HOSTS:
            return self._whois_active
        else:
            raise AttributeError(ErrorCodes.e10140.value)

    def set_whois_active(self, data, update=True):
        """ """
        if self._resource_type == ResourceType.HOSTS:
            self._whois_active = self._uni(data)
        else:
            raise AttributeError(ErrorCodes.e10140.value)

        if update and self._phase == 0:
            self._phase = 2

    #
    # methods
    #
    @property
    def request_uris(self):
        return self._request_uris

    def add_request_uri(self, data):
        """ """
        if data not in self._request_uris:
            self._request_uris.append(data)

    #
    # attributes
    #
    @property
    def attributes(self):
        """ """
        return self._attributes

    def add_attribute(self, data_obj):
        """collection of attributes objects"""
        self._attributes.append(data_obj)

    # #
    # # group object (adversaries, emails, incidents, documents, victims)
    # #
    # @property
    # def groups(self):
    #     """ """
    #     return self._groups
    #
    # def add_group(self, data_obj):
    #     """collection of associated group objects"""
    #     self._groups.append(data_obj)

    #
    # security label
    #
    @property
    def security_label(self):
        """ """
        return self._security_label

    def set_security_label(self, data_obj):
        self.add_security_label(data_obj)

    def add_security_label(self, data_obj):
        """security label"""
        self._security_label.append(data_obj)

    #
    # tags
    #
    @property
    def tags(self):
        """ """
        return self._tags

    def add_tag(self, data_obj):
        """collection of tag objects"""
        self._tags.append(data_obj)

    #
    # phase
    #
    @property
    def phase(self):
        """ """
        return self._phase

    def set_phase(self, data):
        """ """
        self._phase = data

    #
    # resource_type
    #
    @property
    def resource_type(self):
        """ """
        return self._resource_type

    # def set_resource_type(self, data):
    #     """ """
    #     self._resource_type = data

    #
    # validate
    #
    @property
    def validate(self):
        """ validate all required fields """
        for prop, values in self._properties.items():
            # special check for file hash
            if prop in ['_md5', '_sha1', '_sha256']:
                # if any hash is not None then proceed
                if self._md5 or self._sha1 or self._sha256:
                    continue

            if values['required']:
                # fail validation if any required field is None
                if getattr(self, prop) is None:
                    return False

        # validated
        return True

    #
    # add print method
    #
    def __str__(self):
        """allow object to be displayed with print"""

        printable_string = '\n{0!s:_^80}\n'.format('Resource Object Properties')

        #
        # retrievable methods
        #
        printable_string += '{0!s:40}\n'.format('Retrievable Methods')
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('id', self.id))
        if isinstance(self.indicator, dict):
            printable_string += ('  {0!s:<28} {1!s:<50}\n'.format('indicator', ''))
            printable_string += ('   {0!s:<10}: {1!s:<70}\n'.format('md5', self.indicator['md5']))
            printable_string += ('   {0!s:<10}: {1!s:<70}\n'.format('sha1', self.indicator['sha1']))
            printable_string += ('   {0!s:<10}: {1!s:<70}\n'.format('sha256', self.indicator['sha256']))
        else:
            printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('indicator', self.indicator))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('resource_type', self.resource_type))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('owner_name', self.owner_name))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('date_added', self.date_added))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('last_modified', self.last_modified))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('description', self.description))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('confidence', self.confidence))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('rating', self.rating))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('threat_assess_confidence',
                                                               self.threat_assess_confidence))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('threat_assess_rating', self.threat_assess_rating))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('security_label', self.security_label))
        # printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('type', self.type))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('weblink', self.weblink))

        #
        # writable methods
        #
        printable_string += '\n{0!s:40}\n'.format('Writable Properties')
        for prop, values in sorted(self._properties.items()):
            printable_string += ('  {0!s:<28}: {1:<50}\n'.format(
                values['api_field'], '{0!s} (Required: {1!s})'.format(values['method'], str(values['required']))))

        #
        # object information
        #
        printable_string += '\n{0!s:40}\n'.format('Object Information')
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('phase', self.phase))

        #
        # matched filter
        #
        if len(self.matched_filters) > 0:
            printable_string += '\n{0!s:40}\n'.format('Matched Filters')
            for item in sorted(self.matched_filters):
                printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('matched filter', item))

        #
        # request uri's
        #
        if len(self.request_uris) > 0:
            printable_string += '\n{0!s:40}\n'.format('Request URI\'s')
            for item in sorted(self.request_uris):
                printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('', item))

        return printable_string


class IndicatorObjectAdvanced(IndicatorObject):
    """ Temporary Object with extended functionality. """
    __slots__ = (
        '_resource_container',
        '_resource_obj',
        '_resource_properties',
        '_basic_structure',
        '_structure',
        '_tc',
    )

    def __init__(self, tc_obj, resource_container, resource_obj):
        """ add methods to resource object """
        super(IndicatorObject, self).__init__()

        # dynamically set resource properties to the appropriate dictionary in ApiProperties
        self._resource_properties = ApiProperties.api_properties[resource_obj.resource_type.name]['properties']

        self._resource_container = resource_container
        self._resource_obj = resource_obj
        self._basic_structure = {
            'confidence': 'confidence',
            'dateAdded': 'date_added',
            'description': 'description',
            'id': 'id',
            'indicator': 'indicator',
            'lastModified': 'last_modified',
            'ownerName': 'owner_name',
            'rating': 'rating',
            'type': 'type',
            'weblink': 'weblink',
        }
        self._structure = self._basic_structure.copy()
        del self._structure['indicator']  # clear up generic indicator name
        self._tc = tc_obj

        # load data from resource_obj
        self.load_data(self._resource_obj)

        #
        # indicator structure
        #
        if self._resource_type == ResourceType.ADDRESSES:
            self._structure['ip'] = 'indicator'
        elif self._resource_type == ResourceType.EMAIL_ADDRESSES:
            self._structure['address'] = 'indicator'
        elif self._resource_type == ResourceType.FILES:
            self._structure['md5'] = 'indicator'
            self._structure['sha1'] = 'indicator'
            self._structure['sha256'] = 'indicator'
            self._structure['size'] = 'size'
        elif self._resource_type == ResourceType.HOSTS:
            self._structure['dnsActive'] = 'dns_active'
            self._structure['hostName'] = 'indicator'
            self._structure['whoisActive'] = 'whois_active'
        elif self._resource_type == ResourceType.URLS:
            self._structure['source'] = 'source'
            self._structure['text'] = 'indicator'

    def add_attribute(self, attr_type, attr_value, attr_displayed='true'):
        """ add an attribute to an indicator """
        attr_type = self._uni(attr_type)
        attr_value = self._uni(attr_value)
        prop = self._resource_properties['attribute_add']
        ro = RequestObject()
        ro.set_body(json.dumps({
            'type': attr_type,
            'value': attr_value,
            'displayed': attr_displayed}))
        try:
            ro.set_description('add attribute type "{0}" with value "{1}" to {2}'.format(
                attr_type,
                attr_value.encode('ascii', 'ignore'),
                self._reference_indicator.encode('utf-8', 'ignore')))
        except:
            ro.set_description('add attribute type "{0}" with value "unencodable" to {1}'.format(
                attr_type,
                self._reference_indicator.encode('utf-8', 'ignore')))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(self._reference_indicator))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)
        callback = lambda status: self.__add_attribute_failure(attr_type, attr_value)
        ro.set_failure_callback(callback)
        self._resource_container.add_commit_queue(self.id, ro)
        attribute = AttributeObject(self)
        attribute.set_type(attr_type)
        attribute.set_value(attr_value)
        attribute.set_displayed(attr_displayed)
        self._resource_obj.add_attribute(attribute)

    def __add_attribute_failure(self, attr_type, attr_value):
        for attribute in self._attributes:
            if attribute.type == attr_type and attribute.value == attr_value:
                self._attributes.remove(attribute)
                break

    def add_file_occurrence(self, fo_file_name=None, fo_path=None, fo_date=None):
        """ add an file occurrence to an indicator """
        if self._resource_type != ResourceType.FILES:
            raise AttributeError(ErrorCodes.e10150.value)

        prop = self._resource_properties['file_occurrence_add']
        ro = RequestObject()
        json_dict = {}
        if fo_file_name is not None:
            json_dict['fileName'] = fo_file_name
        if fo_path is not None:
            json_dict['path'] = fo_path
        if fo_date is not None:
            json_dict['date'] = fo_date
        ro.set_body(json.dumps(json_dict))
        ro.set_description('add file occurrence - file "{0}" to "{1}"'.format(fo_file_name.encode('ascii', 'ignore'), self._reference_indicator))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(self._reference_indicator))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)
        self._resource_container.add_commit_queue(self.id, ro)

    def add_tag(self, tag):
        """ add a tag to an indicator """
        prop = self._resource_properties['tag_add']
        ro = RequestObject()
        ro.set_description('add tag "{0}" to {1}'.format(tag, self._reference_indicator))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(
            self._reference_indicator, self._urlsafe(tag)))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)
        self._resource_container.add_commit_queue(self.id, ro)

    def associate_group(self, resource_type, resource_id):
        """ associate a group to indicator by id """
        prop = self._resource_properties['association_group_add']
        ro = RequestObject()
        ro.set_description('associate group type "{0}" id {1} to {2}'.format(
            resource_type.name, resource_id, self._reference_indicator))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_resource_pagination(prop['pagination'])
        group_uri_attribute = ApiProperties.api_properties[resource_type.name]['uri_attribute']
        ro.set_request_uri(prop['uri'].format(
            self._reference_indicator, group_uri_attribute, resource_id))
        ro.set_resource_type(self._resource_type)
        self._resource_container.add_commit_queue(self.id, ro)

    @property
    def gen_body(self):
        """ generate json body for POST and PUT API requests """
        body_dict = {}
        for prop, values in self._properties.items():
            if getattr(self, prop) is not None:
                body_dict[values['api_field']] = getattr(self, prop)
        return json.dumps(body_dict)

    @property
    def cef(self):
        """ return indicator in CEF format """

        # Version - integer
        cef_version = '0'

        # Vendor - string
        cef_device_vendor = 'threatconnect'

        # Product - string
        cef_device_product = 'threatconnect'

        # Product Version - integer
        cef_product_version = 2

        # CEF Signature (id) - string (in this case id is integer)
        cef_signature_id = self.id

        # Severity - integer
        # The value should be integer 1-10 with 10 be highest.
        # If threatconnect only goes up to 5 some modifications might be a good idea.
        # This could be an algorithm between rating and confidence
        if self.rating is not None:
            cef_severity = (self.rating * 2)
        else:
            cef_severity = 0

        # CEF Name (description) - string
        if self.description is not None:
            cef_name = self.description
        else:
            cef_name = "null"

        #
        # CEF Extension
        #
        cef_extension = ""

        for k, v in sorted(self._structure.items()):
            # handle file indicators
            if k == 'md5':
                cef_extension += '{0}="{1}" '.format(k, getattr(self, v)['md5'])
            elif k == 'sha1':
                cef_extension += '{0}="{1}" '.format(k, getattr(self, v)['sha1'])
            elif k == 'sha256':
                cef_extension += '{0}="{1}" '.format(k, getattr(self, v)['sha256'])
            elif k == 'description':
                continue  # used above
            elif k == 'id':
                continue  # used above
            elif k == 'rating':
                continue  # used above
            else:
                cef_extension += '{0}="{1}" '.format(k, self.cef_format_extension(getattr(self, v)))

        # Build CEF String
        return "CEF:{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}".format(
            cef_version, cef_device_vendor, cef_device_product, cef_product_version,
            cef_signature_id, cef_name, cef_severity, cef_extension)

    # @staticmethod
    # def cef_format_prefix(data):
    #     formatted = data.replace('|', '\|').replace('"\"', '\\')
    #     return formatted

    @staticmethod
    def cef_format_extension(data):
        if data is None or isinstance(data, (int, float)):
            return data
        else:
            formatted = data.replace('"\"', '\\').replace('=', '\=')
        return formatted

    def commit(self):
        """ commit indicator and related associations, attributes, security labels and tags """
        r_id = self.id
        ro = RequestObject()
        ro.set_body(self.gen_body)
        if self.owner_name is not None:
            ro.set_owner(self.owner_name)
        ro.set_resource_type(self.resource_type)
        if self.phase == 1:
            prop = self._resource_properties['add']
            ro.set_description('adding indicator {0}.'.format(self._reference_indicator))
            ro.set_http_method(prop['http_method'])
            ro.set_owner_allowed(prop['owner_allowed'])
            ro.set_request_uri(prop['uri'].format(self._reference_indicator))
            ro.set_resource_pagination(prop['pagination'])
            # validate all required fields are present
            if self.validate:
                api_response = self._tc.api_request(ro)
                if api_response.headers['content-type'] == 'application/json':
                    api_response_dict = api_response.json()
                    if api_response_dict['status'] == 'Success':
                        resource_key = ApiProperties.api_properties[self.resource_type.name]['resource_key']
                        r_id = api_response_dict['data'][resource_key]['id']
            else:
                self._tc.tcl.debug('Resource Object'.format(self))
                raise AttributeError(ErrorCodes.e10040.value)
        elif self.phase == 2:
            prop = self._resource_properties['update']
            ro.set_description('update indicator {0}.'.format(self._reference_indicator))
            ro.set_http_method(prop['http_method'])
            ro.set_owner_allowed(prop['owner_allowed'])
            ro.set_request_uri(prop['uri'].format(self._reference_indicator))
            ro.set_resource_pagination(prop['pagination'])
            api_response = self._tc.api_request(ro)
            if api_response.headers['content-type'] == 'application/json':
                api_response_dict = api_response.json()
                if api_response_dict['status'] != 'Success':
                    self._tc.tcl.error('API Request Failure: [{0}]'.format(ro.description))

        # submit all attributes, tags or associations
        for ro in self._resource_container.commit_queue(self.id):
            if self.owner_name is not None:
                ro.set_owner(self.owner_name)
            # replace the id
            if self.phase == 1 and self.id != r_id:
                request_uri = str(ro.request_uri.replace(str(self.id), str(r_id)))
                ro.set_request_uri(request_uri)
            api_response2 = self._tc.api_request(ro)
            if api_response2.headers['content-type'] == 'application/json':
                api_response_dict2 = api_response2.json()
                if api_response_dict2['status'] != 'Success':
                    self._tc.tcl.error('API Request Failure: [{0}]'.format(ro.description))

        if r_id is not None:
            self.set_id(r_id)

        self._resource_container.clear_commit_queue_id(self.id)

        self.set_phase(0)

        if self._reload_attributes:
            self.load_attributes(automatically_reload=True)

        # return object
        return self

    @property
    def csv(self):
        """ return the object in json format """

        indicator = None
        csv_dict = {'indicator': None}
        for k, v in self._basic_structure.items():
            # skip indicator and handle outside of loop
            if k == 'indicator':
                indicator = getattr(self, v)
                continue
            csv_dict[k] = getattr(self, v)

        outfile = StringIO()
        writer = csv.DictWriter(outfile, quotechar='"', fieldnames=sorted(csv_dict.keys()))

        if isinstance(indicator, dict):
            for k, v in indicator.items():
                if v is not None:
                    csv_dict['indicator'] = v
                    writer.writerow(csv_dict)
        else:
            csv_dict['indicator'] = indicator
            writer.writerow(csv_dict)

        return outfile.getvalue().rstrip()

    @property
    def csv_header(self):
        """ return the object in json format """

        csv_dict = {}
        for k, v in self._basic_structure.items():
            csv_dict[k] = v

        outfile = StringIO()
        # not supported in python 2.6
        # writer = csv.DictWriter(outfile, fieldnames=sorted(csv_dict.keys()))
        # writer.writeheader()

        csv_header = ','.join(sorted(csv_dict.keys()))
        outfile.write(csv_header)

        return outfile.getvalue().rstrip()

    def delete(self):
        """ delete indicator """
        prop = self._resource_properties['delete']
        ro = RequestObject()
        ro.set_description('delete indicator {0}.'.format(self._reference_indicator))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        if self.owner_name is not None:
            ro.set_owner(self.owner_name)
        ro.set_request_uri(prop['uri'].format(self._reference_indicator))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self.resource_type)
        self._tc.api_request(ro)
        self.set_phase(3)

    def delete_attribute(self, attr_id):
        """ delete attribute from indicator by id """
        prop = self._resource_properties['attribute_delete']
        ro = RequestObject()
        ro.set_description('delete attribute id {0} from {1}'.format(attr_id, self._reference_indicator))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(
            self._reference_indicator, attr_id))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)
        self._resource_container.add_commit_queue(self.id, ro)

    def delete_security_label(self, label):
        """ set the security label for this indicator """
        prop = self._resource_properties['security_label_delete']
        ro = RequestObject()
        ro.set_description('delete security label "{0}" from {1}'.format(label, self._reference_indicator))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(
            self._reference_indicator, self._urlsafe(label)))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)
        self._resource_container.add_commit_queue(self.id, ro)

    def delete_tag(self, tag):
        """ delete tag from indicator """
        prop = self._resource_properties['tag_delete']
        ro = RequestObject()
        ro.set_description('delete tag "{0}" from {1}'.format(tag, self._reference_indicator))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(
            self._reference_indicator, self._urlsafe(tag)))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)
        self._resource_container.add_commit_queue(self.id, ro)

    def disassociate_group(self, resource_type, resource_id):
        """ disassociate group from indicator """
        prop = self._resource_properties['association_group_delete']
        ro = RequestObject()
        ro.set_description('disassociate group type {0} id {1} from {2}'.format(
            resource_type.name, resource_id, self._reference_indicator))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        group_uri_attribute = ApiProperties.api_properties[resource_type.name]['uri_attribute']
        ro.set_request_uri(prop['uri'].format(
            self._reference_indicator, group_uri_attribute, resource_id))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)

        self._resource_container.add_commit_queue(self.id, ro)

    @property
    def group_associations(self):
        """ retrieve associations for this indicator. associations are not stored within the object """
        prop = self._resource_properties['association_groups']
        ro = RequestObject()
        ro.set_description('retrieve group associations for {0}'.format(self._reference_indicator))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(self._reference_indicator))
        ro.set_owner(self.owner_name)
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)

        for item in self._tc.result_pagination(ro, 'group'):
            yield GroupObject.parse_group(item, api_filter=ro.description, request_uri=ro.request_uri)

    @property
    def indicator_associations(self):
        """ retrieve associations for this indicator. associations are not stored within the object """
        prop = self._resource_properties['association_indicators']
        ro = RequestObject()
        ro.set_description('retrieve indicator associations for {0}'.format(self._reference_indicator))
        ro.set_http_method(prop['http_method'])
        ro.set_owner(self.owner_name)
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(self._reference_indicator))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)

        for item in self._tc.result_pagination(ro, 'indicator'):
            yield parse_indicator(
                item, api_filter=ro.description, request_uri=ro.request_uri, indicators_regex=self._tc._indicators_regex)

    @property
    def json(self):
        """ return the object in json format """
        json_dict = {}
        for k, v in self._structure.items():
            # handle file indicators
            if k == 'md5':
                json_dict[k] = getattr(self, v)['md5']
            elif k == 'sha1':
                json_dict[k] = getattr(self, v)['sha1']
            elif k == 'sha256':
                json_dict[k] = getattr(self, v)['sha256']
            else:
                json_dict[k] = getattr(self, v)

        return json.dumps(json_dict, indent=4, sort_keys=True)

    @property
    def keyval(self):
        """ return the object in json format """
        keyval_str = ''
        for k, v in sorted(self._structure.items()):
            # handle file indicators
            if k == 'md5':
                keyval_str += '{0}="{1}" '.format(k, getattr(self, v)['md5'])
            elif k == 'sha1':
                keyval_str += '{0}="{1}" '.format(k, getattr(self, v)['sha1'])
            elif k == 'sha256':
                keyval_str += '{0}="{1}" '.format(k, getattr(self, v)['sha256'])
            else:
                keyval_str += '{0}="{1}" '.format(k, getattr(self, v))

        return keyval_str

    @property
    def leef(self):
        """ return indicator in LEEF format """

        """
        https://www-01.ibm.com/support/knowledgecenter/SSMPHH_9.1.0/com.ibm.guardium91.doc/
            appendices/topics/leef_mapping.html

        example:
        Jan 18 11:07:53 host LEEF:Version|Vendor|Product|Version|EventID|
        Key1=Value1<tab>Key2=Value2<tab>Key3=Value3<tab>...<tab>KeyN=ValueN

        Jan 18 11:07:53 192.168.1.1 LEEF:1.0|QRadar|QRM|1.0|NEW_PORT_DISCOVERD|
        src=172.5.6.67 dst=172.50.123.1 sev=5 cat=anomaly msg=there are spaces in this message
        """

        # Version - integer
        leef_version = '0'

        # Vendor - string
        leef_device_vendor = 'threatconnect'

        # Product - string
        leef_device_product = 'threatconnect'

        # Product Version - integer
        leef_product_version = 2

        # LEEF Signature (id) - string (in this case id is integer)
        leef_event_id = self.id

        #
        # LEEF Extension
        #
        leef_extension = ""

        for k, v in sorted(self._structure.items()):
            # handle file indicators
            if k == 'md5':
                leef_extension += '{0}="{1}" '.format(k, getattr(self, v)['md5'])
            elif k == 'sha1':
                leef_extension += '{0}="{1}" '.format(k, getattr(self, v)['sha1'])
            elif k == 'sha256':
                leef_extension += '{0}="{1}" '.format(k, getattr(self, v)['sha256'])
            elif k == 'dateAdded':
                leef_extension += '{0}="{1}" '.format('devTime', getattr(self, v))
            elif k == 'rating':
                leef_extension += '{0}="{1}" '.format('severity', getattr(self, v))
            else:
                leef_extension += '{0}="{1}" '.format(k, getattr(self, v))

        # Build LEEF String
        return "LEEF:{0}|{1}|{2}|{3}|{4}|{5}".format(
            leef_version, leef_device_vendor, leef_device_product,
            leef_product_version, leef_event_id, leef_extension)

    def load_attributes(self, automatically_reload=False):
        self._reload_attributes = automatically_reload
        """ retrieve attributes for this indicator """
        prop = self._resource_properties['attributes']
        ro = RequestObject()
        ro.set_description('load attributes for {0}'.format(self._reference_indicator))
        ro.set_http_method(prop['http_method'])
        ro.set_owner(self.owner_name)
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(self._reference_indicator))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)
        api_response = self._tc.api_request(ro)

        if api_response.headers['content-type'] == 'application/json':
            api_response_dict = api_response.json()
            if api_response_dict['status'] == 'Success':
                data = api_response_dict['data']['attribute']
                self._resource_obj._attributes = []
                for item in data:
                    self._resource_obj.add_attribute(parse_attribute(item, self))  # add to main resource object

    def load_data(self, resource_obj):
        """ load data from resource object to self """
        for key in resource_obj.__slots__:
            setattr(self, key, getattr(resource_obj, key))

    def load_dns_resolutions(self):
        """ retrieve dns resolution for this indicator """
        if self._resource_type != ResourceType.HOSTS:
            raise AttributeError(ErrorCodes.e10110.value)

        prop = self._resource_properties['dns_resolution']
        ro = RequestObject()
        ro.set_description('load dns resolution for {0}'.format(self._reference_indicator))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_resource_pagination(prop['pagination'])
        ro.set_request_uri(prop['uri'].format(self._reference_indicator))
        ro.set_owner(self.owner_name)
        ro.set_resource_type(ResourceType.DNS_RESOLUTIONS)

        data = self._tc.api_response_handler(self, ro)
        for item in data:
                self._resource_obj.add_dns_resolution(item)  # add to main resource object

    def load_file_occurrence(self):
        """ retrieve file occurrence for this indicator """
        if self._resource_type != ResourceType.FILES:
            raise AttributeError(ErrorCodes.e10120.value)

        prop = self._resource_properties['file_occurrences']
        ro = RequestObject()
        ro.set_description('load file occurrence for {0}'.format(self._reference_indicator))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_resource_pagination(prop['pagination'])
        ro.set_request_uri(prop['uri'].format(self._reference_indicator))
        ro.set_owner(self.owner_name)
        ro.set_resource_type(self._resource_type)
        api_response = self._tc.api_request(ro)

        if api_response.headers['content-type'] == 'application/json':
            api_response_dict = api_response.json()
            if api_response_dict['status'] == 'Success':
                data = api_response_dict['data']['fileOccurrence']
                for item in data:
                    self._resource_obj.add_file_occurrence(parse_file_occurrence(item))  # add to main resource object

    def load_security_label(self):
        """ retrieve security label for this indicator """
        prop = self._resource_properties['security_label_load']
        ro = RequestObject()
        ro.set_description('load security labels for {0}'.format(self._reference_indicator))
        ro.set_http_method(prop['http_method'])
        ro.set_owner(self.owner_name)
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(self._reference_indicator))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)
        api_response = self._tc.api_request(ro)

        if api_response.headers['content-type'] == 'application/json':
            api_response_dict = api_response.json()
            if api_response_dict['status'] == 'Success':
                data = api_response_dict['data']['securityLabel']
                for item in data:
                    self._security_label = parse_security_label(item)  # add to main resource object

    def load_tags(self):
        """ retrieve tags for this indicator """
        prop = self._resource_properties['tags_load']
        ro = RequestObject()
        ro.set_description('load tags for {0}'.format(self._reference_indicator))
        ro.set_http_method(prop['http_method'])
        ro.set_owner(self.owner_name)
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(self._reference_indicator))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)
        api_response = self._tc.api_request(ro)

        if api_response.headers['content-type'] == 'application/json':
            api_response_dict = api_response.json()
            if api_response_dict['status'] == 'Success':
                data = api_response_dict['data']['tag']
                for item in data:
                    self._resource_obj.add_tag(parse_tag(item))  # add to main resource object

    def set_security_label(self, label):
        self.add_security_label(label)

    def add_security_label(self, label):
        """ set the security label for this indicator """
        prop = self._resource_properties['security_label_add']
        ro = RequestObject()
        ro.set_description('add security label "{0}" to {1}'.format(label, self._reference_indicator))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_resource_pagination(prop['pagination'])
        ro.set_request_uri(prop['uri'].format(
            self._reference_indicator, self._urlsafe(label)))
        ro.set_resource_type(self._resource_type)

        self._resource_container.add_commit_queue(self.id, ro)

    def update_attribute(self, attr_id, attr_value):
        """ update indicator attribute by id """
        attr_value = self._uni(attr_value)
        prop = self._resource_properties['attribute_update']
        ro = RequestObject()
        ro.set_body(json.dumps({'value': attr_value}))
        try:
            ro.set_description('update attribute id {0} with value "{1}" on {2}'.format(
                attr_id,
                attr_value,
                self._reference_indicator))
        except:
            ro.set_description('update attribute id {0} with value "unencodable" on {1}'.format(
                attr_id,
                self._reference_indicator))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_request_uri(prop['uri'].format(
            self._reference_indicator, attr_id))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)

        self._resource_container.add_commit_queue(self.id, ro)

    @property
    def victim_associations(self):
        """ retrieve associations for this indicator. associations are not stored within the object """
        prop = self._resource_properties['association_victims']
        ro = RequestObject()
        ro.set_description('retrieve victim associations for {0}'.format(self._reference_indicator))
        ro.set_http_method(prop['http_method'])
        ro.set_owner_allowed(prop['owner_allowed'])
        ro.set_owner(self.owner_name)
        ro.set_request_uri(prop['uri'].format(self._reference_indicator))
        ro.set_resource_pagination(prop['pagination'])
        ro.set_resource_type(self._resource_type)

        for item in self._tc.result_pagination(ro, 'victim'):
            yield parse_victim(item, api_filter=ro.description, request_uri=ro.request_uri)

    #
    # attributes
    #
    @property
    def attributes(self):
        """ """
        return self._resource_obj._attributes
