def parse_file_occurrence(fo_dict):
    """ """
    fo = FileOccurrenceObject()

    #
    # standard values
    #
    if 'date' in fo_dict:
        fo.set_date(fo_dict['date'])
    if 'fileName' in fo_dict:
        fo.set_file_name(fo_dict['fileName'])
    if 'path' in fo_dict:
        fo.set_path(fo_dict['path'])

    return fo


class FileOccurrenceObject(object):
    __slots__ = (
        '_date',
        '_file_name',
        '_path',
    )

    def __init__(self):
        self._date = None
        self._file_name = None
        self._path = None

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

    """ shared file occurrence methods """

    #
    # date
    #
    @property
    def date(self):
        """ """
        return self._date

    def set_date(self, data):
        """Read-Write file occurrence metadata"""
        self._date = data

    #
    # file name
    #
    @property
    def file_name(self):
        """ """
        return self._file_name

    def set_file_name(self, data):
        """Read-Write file occurrence metadata"""
        self._file_name = data

    #
    # path
    #
    @property
    def path(self):
        """ """
        return self._path

    def set_path(self, data):
        """Read-Write file occurrence metadata"""
        self._path = data

    #
    # add print method
    #
    def __str__(self):
        """allow object to be displayed with print"""

        printable_string = '\n{0!s:_^80}\n'.format('File Occurrence Object Properties')

        #
        # retrievable methods
        #
        printable_string += '{0!s:40}\n'.format('Retrievable Methods')
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('file_name', self.file_name))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('date', self.date))
        printable_string += ('  {0!s:<28}: {1!s:<50}\n'.format('path', self.path))

        return printable_string
