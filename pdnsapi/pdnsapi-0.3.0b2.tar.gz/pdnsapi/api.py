import json
from urlparse import urljoin, urlparse

from requests import delete, get, patch, post

from requests.exceptions import ChunkedEncodingError

from pdnsapi.exceptions import (
    PDNSAccessDeniedException, PDNSNotFoundException,
    PDNSProtocolViolationException, PDNSServerErrorException,
    PDNSException)

DEFAULT_TTL = 60


class _APIKeyManager(object):
    """ Module specific singelton class, to avoid having to pass around API
    keys between instances.
    """
    __single_instance = None

    def __init__(self):
        self.__keys = {}

    @classmethod
    def get_instance(cls):
        if cls.__single_instance is None:
            cls.__single_instance = cls()

        return cls.__single_instance

    def add_key(self, url, key):
        self.__keys[self.__hash_url(url)] = key

    def get_key(self, url):
        return self.__keys[self.__hash_url(url)]

    @staticmethod
    def __hash_url(url):
        parsed_url = urlparse(url)
        return parsed_url.netloc


class Record(object):
    """ Representation of a DNS record """
    def __init__(self, name, type_, records, ttl=DEFAULT_TTL):
        self.name = name
        self.type = type_
        self.records = records
        self.ttl = ttl

    def __repr__(self):
        return '<{0} object: {1} {2}>'.format(self.__class__.__name__,
                                              self.type, self.name)

    def change_zone(self, old_zone_name, new_zone_name):
        self.name = self.__replace_last(
            self.name, old_zone_name, new_zone_name)

    @property
    def dict_representation(self):
        return {
                'records': [
                    {
                        'content': record,
                        'disabled': False
                    } for record in self.records],
                'name': self.name,
                'ttl': self.ttl,
                'type': self.type
            }

    @staticmethod
    def __replace_last(source, replace_what, replace_with):
        head, sep, tail = source.rpartition(replace_what)
        return head + replace_with + tail


class Resource(object):
    """ Superclass for DNS resources: root resources and zones """

    @staticmethod
    def perform_request(method, url, data=None):
        """
        Perform a request against the PowerDNS REST API.

        :param method: The HTTP method to use, as a requests function.
        :type method: function
        :param url: The URL of the endpoint to request.
        :param url: string
        :param data: JSON formatted data to send in the request.
        :type data: string
        :return: JSON-parsed data that is returned by the API.
        :rtype: dict
        """
        api_key = _APIKeyManager.get_instance().get_key(url)
        response = method(url, headers={'X-API-Key': api_key}, data=data)
        parsed_response = None

        if ('Content-Type' in response.headers and
                response.headers['Content-Type'] == 'application/json'):
            parsed_response = response.json()

        if response.status_code == 401:
            raise PDNSAccessDeniedException(response.text)
        elif response.status_code == 404:
            raise PDNSNotFoundException(response.text)
        elif response.status_code == 422:
            raise PDNSProtocolViolationException(parsed_response['error'])
        elif response.status_code == 500:
            raise PDNSServerErrorException()
        elif response.status_code not in (200, 201, 204):
            raise PDNSException()

        if parsed_response is not None:
            return parsed_response


class Zone(Resource):
    """ Representation of a DNS Zone """
    def __init__(self, name, records, url):
        self.name = name
        self.url = url
        self.__update_records(records)

    @property
    def records(self):
        """
        Return all records in the zone.

        :return: All records in the zone
        :rtype: list
        """
        return self.__record_list

    def get_record(self, name, type_):
        """
        Return a record, specified by name and type.

        :param name: The name of the sought record.
        :type name: string
        :param type_:
        :type type_: The type of the sought record.
        :return: The sought record.
        :rtype: Record
        """
        for record in self.records:
            if record.name == name and record.type == type_:
                return record

        raise PDNSNotFoundException('Record not found')

    def add_record(self, record):
        """
        Add a new record in the zone.

        :param record: The record to add to the zone.
        :type record: Record
        """
        self.update_record(record.name, record.type, record)

    def update_record(self, current_name, current_type, new_record):
        """
        Update an existing record in the zone.

        :param current_name: The current name of the record
        :type current_name: str
        :param current_type: The current type of the record
        :type current_type: str
        :param new_record: The new record
        :type new_record: Record
        """

        data = Zone.__format_record_data('REPLACE', new_record, current_name,
                                         current_type)
        data['rrsets'][0]['name'] = current_name
        data['rrsets'][0]['records'][0]['name'] = new_record.name
        data['rrsets'][0]['records'][0]['type'] = new_record.type
        data['rrsets'][0]['records'][0]['ttl'] = new_record.ttl
        data['rrsets'][0]['records'][0]['disabled'] = False

        updated_zone = Resource.perform_request(patch, self.url,
                                                data=json.dumps(data))

        self.__update_records(updated_zone['rrsets'])

    def delete_record(self, record):
        """
        Delete a record from the zone.

        :param record: The record to remove from the zone.
        :type record: record
        """
        data = Zone.__format_record_data('DELETE', record)

        updated_zone = Resource.perform_request(patch, self.url,
                                                data=json.dumps(data))

        self.__update_records(updated_zone['rrsets'])

    @staticmethod
    def __format_record_data(change_type,
                             record,
                             current_name=None,
                             current_type=None):

        data = record.dict_representation

        data['changetype'] = change_type

        return {'rrsets': [data]}

    def __update_records(self, records):
        self.__record_list = []

        for record in records:
            record_content = [r['content'] for r in record['records']]
            self.__record_list.append(
                Record(record['name'], record['type'], record_content,
                       record['ttl'])
            )

    def __repr__(self):
        return '<{0} object: {1}>'.format(self.__class__.__name__, self.name)


class RootResource(Resource):
    """ The server's root resource, responsible for crud-operations on
        zones """
    def __init__(self, zones_url):
        self.zones_url = zones_url

        parsed_url = urlparse(zones_url)
        self.root_url = '{0}://{1}'.format(parsed_url.scheme,
                                           parsed_url.netloc)

    def get_zone(self, zone_name):
        """
        Fetch a zone from the DNS server specified by name.

        :param zone_name: The name of the zone to fetch.
        :type zone_name: string
        :return: The created zone
        :rtype: Zone
        """
        zone_data = Resource.perform_request(get, urljoin(self.zones_url + '/',
                                                          zone_name))
        return Zone(zone_data['name'],
                    zone_data['rrsets'],
                    urljoin(self.root_url + '/', zone_data['url']))

    @property
    def zones(self):
        """
        Fetch all zones on the server.

        :return: All zones on the server.
        :rtype: list
        """
        result = []
        zones = self.perform_request(get, self.zones_url)
        for zone in zones:
            expanded_zone = self.get_zone(zone['name'])
            result.append(expanded_zone)

        return result

    def create_zone(self, name, name_servers=None, records=None):
        """
        Create a new zone on the DNS server.

        :param name: The canonical name of the new zone.
        :type name: string
        :param name_servers: The name servers to use.
        :type name_servers: list
        :return: The created zone
        :rtype: Zone
        """
        if name_servers is None:
            name_servers = []
        if records is None:
            records = []
        data = {
            'name': name,
            'kind': "Native",
            'masters': [],
            'nameservers': name_servers,
            'rrsets': records
        }

        zone_data = self.perform_request(post, self.zones_url,
                                         data=json.dumps(data))

        return Zone(zone_data['name'],
                    zone_data['rrsets'],
                    urljoin(self.root_url + '/', zone_data['url']))

    def delete_zone(self, zone_name):
        """
        Delete a zone from the DNS server.

        :param zone_name:
        :return:
        """
        try:
            self.perform_request(delete, '{0}/{1}'.format(
                self.zones_url, zone_name))
        except ChunkedEncodingError as e:
            # Power DNS sometimes fails to respond properly on delete.
            # the zone is deleted though.
            pass

    def rename_zone(self, zone, new_name):
        """
        Rename a zone.
        :param zone:
        :param new_name:
        :return: The zone with a new name.
        """
        self.delete_zone(zone.name)
        records = []
        for record in zone.records:
            record.change_zone(zone.name, new_name)
            records.append(record.dict_representation)

        return self.create_zone(new_name, records=records)

    def change_record_zone(self, record, source, target):
        source.delete_record(record)
        record.change_zone(source.name, target.name)
        target.add_record(record)


def init_api(url, server_id, key):
    """
    Create a new api connection to the server and return the RootResource.

    :param url: The url of the server
    :type url: string
    :param server_id: The server id
    :type server_id: string
    :param key: The API Key
    :type key: string
    :return: A root resource for operating on the DNS server
    :rtype: RootResource
    """
    _APIKeyManager.get_instance().add_key(url, key)

    return RootResource('{0}/api/v1/servers/{1}/zones'.format(url, server_id))
