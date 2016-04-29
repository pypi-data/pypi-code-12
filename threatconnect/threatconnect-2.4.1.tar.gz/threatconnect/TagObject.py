def parse_tag(tag_dict):
    """ """
    tag = TagObject()

    #
    # standard values
    #
    tag.set_name(tag_dict['name'])
    tag.set_weblink(tag_dict['webLink'])

    return tag


class TagObject(object):
    __slots__ = (
        '_name',
        '_weblink',
        '_required_attrs',
        '_validated',
        '_writable_attrs',
    )

    def __init__(self):
        self._name = None
        self._required_attrs = ['name']
        self._weblink = None
        self._writable_attrs = {
            '_name': 'set_name',
        }

        # validation
        self._validated = False

    #
    # unicode
    #
    @staticmethod
    def _uni(data):
        """ """
        if isinstance(data, (int, list, dict)):
            return data
        elif isinstance(data, unicode):
            return unicode(data.encode('utf-8').strip(), errors='ignore')  # re-encode poorly encoded unicode
        elif not isinstance(data, unicode):
            return unicode(data, 'utf-8', errors='ignore')
        else:
            return data

    """ shared tag methods """

    #
    # name
    #
    @property
    def name(self):
        """ """
        return self._name

    def set_name(self, data):
        """Read-Write tag metadata"""
        self._name = self._uni(data)

    #
    # weblink
    #
    @property
    def weblink(self):
        """ """
        return self._weblink

    def set_weblink(self, data):
        """Read-Only tag metadata"""
        self._weblink = data

    #
    # validated
    #
    @property
    def validated(self):
        """ """
        return self._validated

    def validate(self):
        """ """
        for required in self._required_attrs:
            if getattr(self, required) is None:
                self._validated = False
                return

        self._validated = True

    #
    # add print method
    #
    def __str__(self):
        """allow object to be displayed with print"""

        printable_string = '\n{0!s:_^80}\n'.format('Tag Object Properties')

        #
        # retrievable methods
        #
        printable_string += '{0!s:40}\n'.format('Retrievable Methods')
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('name', self.name))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('weblink', self.weblink))

        return printable_string
