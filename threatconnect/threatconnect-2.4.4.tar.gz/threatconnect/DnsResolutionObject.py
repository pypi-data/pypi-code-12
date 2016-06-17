""" standard """
from Config.ResourceType import ResourceType


def parse_dns_resolution(dr_dict):
    """ """
    dr_list = []

    #
    # standard values
    #
    for address in dr_dict['addresses']:
        dr = DnsResolutionObject()
        dr.set_ip(address['ip'])
        dr.set_resolution_date(dr_dict['resolutionDate'])
        dr.set_owner_name(address['ownerName'])
        dr.set_weblink(address['webLink'])
        dr_list.append(dr)

    return dr_list


class DnsResolutionObject(object):
    __slots__ = (
        '_ip',
        '_owner_name',
        '_resolution_date',
        '_weblink',
        'resource_type'
    )

    def __init__(self):
        self._ip = None
        self._owner_name = None
        self._resolution_date = None
        self._weblink = None
        self.resource_type = ResourceType.DNS_RESOLUTIONS

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

    """ shared dns resolution methods """

    #
    # ip
    #
    @property
    def ip(self):
        """ """
        return self._ip

    def set_ip(self, data):
        """Read-Only dns resolution metadata"""
        self._ip = data

    #
    # owner name
    #
    @property
    def owner_name(self):
        """ """
        return self._owner_name

    def set_owner_name(self, data):
        """Read-Only dns resolution metadata"""
        self._owner_name = data

    #
    # resolution date
    #
    @property
    def resolution_date(self):
        """ """
        return self._resolution_date

    def set_resolution_date(self, data):
        """Read-Only dns resolution metadata"""
        self._resolution_date = data

    #
    # weblink
    #
    @property
    def weblink(self):
        """ """
        return self._weblink

    def set_weblink(self, data):
        """Read-Only dns resolution metadata"""
        self._weblink = data

    #
    # add print method
    #
    def __str__(self):
        """allow object to be displayed with print"""

        printable_string = '\n{0!s:_^80}\n'.format('DNS Resolution Object Properties')

        #
        # retrievable methods
        #
        printable_string += '{0!s:40}\n'.format('Retrievable Methods')
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('ip', self.ip))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('owner_name', self.owner_name))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('resolution_date', self.resolution_date))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('weblink', self.weblink))

        return printable_string
