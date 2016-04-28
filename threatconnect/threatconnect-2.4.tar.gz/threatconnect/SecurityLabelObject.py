def parse_security_label(sl_dict):
    """ """
    sl = SecurityLabelObject()

    #
    # standard values
    #
    sl.set_date_added(sl_dict['dateAdded'])
    sl.set_description(sl_dict['description'])
    sl.set_name(sl_dict['name'])

    return sl


class SecurityLabelObject(object):
    __slots__ = (
        '_date_added',
        '_description',
        '_name',
    )

    def __init__(self):
        self._date_added = None
        self._description = None
        self._name = None

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
    # date_added
    #
    @property
    def date_added(self):
        """ """
        return self._date_added

    def set_date_added(self, data):
        """Read-Only dns resolution metadata"""
        self._date_added = self._uni(data)

    #
    # description
    #
    @property
    def description(self):
        """ """
        return self._description

    def set_description(self, data):
        """Read-Only dns resolution metadata"""
        self._description = self._uni(data)

    #
    # name
    #
    @property
    def name(self):
        """ """
        return self._name

    def set_name(self, data):
        """Read-Only dns name metadata"""
        self._name = self._uni(data)

    #
    # add print method
    #
    def __str__(self):
        """allow object to be displayed with print"""

        printable_string = '\n{0!s:_^80}\n'.format('Security Label Properties')

        #
        # retrievable methods
        #
        printable_string += '{0!s:40}\n'.format('Retrievable Methods')
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('name', self.name))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('description', self.description))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('date_added', self.date_added))

        return printable_string
