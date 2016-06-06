from .anyfield import SField

class View(object):
    def __init__(self, fields, caption=None, highlighters=None, **kwargs):
        self._caption = u"View"

        self._fields = []
        self._highlighters = {}

        self.update(fields=fields, caption=caption, highlighters=highlighters, **kwargs)

    def __call__(self, data):
        pass

    def update(self, fields=None, caption=None, highlighters=None, **kwargs):
        """ This method is used to change HTMLTable initial data, thus, changing representation
            Can be used for example, when some function returns partly configured HTMLTable instance,
            but user want's to display more fields for example, or add some custom highlighters

            arguments same as for constructor, except 'recordlist' arg, which is absent in this method

            :return: self
        """
        self._caption = _(self._recordlist) if caption is None else _(caption)
        fields = [] if fields is None else fields
        for field in fields:
            if isinstance(field, HField):
                self._fields.append(field)
            elif isinstance(field, six.string_types):
                self._fields.append(HField(field))
            elif callable(field):
                self._fields.append(HField(field))
            elif isinstance(field, (tuple, list)) and len(field) == 2:
                self._fields.append(HField(field[0], name=field[1]))
            else:
                raise ValueError('Unsupported field type: %s' % repr(field))

        if highlighters is not None:
            self._highlighters.update(highlighters)

        return self

    @property
    def caption(self):
        """ Table caption
        """
        return self._caption

    @property
    def fields(self):
        """ List of fields of table.
            :type: list of HField instances
        """
        return self._fields

    @property
    def iheaders(self):
        """ Iterator in headers
            :type: list of unicode strings
        """
        return (_(field) for field in self.fields)

    @property
    def irecords(self):
        """ Returns iterator on records, where each record
            is dictionary of two fields: 'row', 'color'.

            'row' dictionary field is iterator in fields of this record

            so result of this property colud be used to build representation
        """
        def preprocess_field(field):
            """ Process some special cases of field to be correctly displayed
            """
            if isinstance(field, HTML):
                return field._repr_html_()
            return _(field)

        for record in self._recordlist:
            yield {
                'color': self.highlight_record(record),
                'row': (preprocess_field(field(record)) for field in self.fields),
            }

    def highlight_record(self, record):
        """ Checks all highlighters related to this representation object
            and return color of firest match highlighter
        """
        for color, highlighter in self._highlighters.items():
            if highlighter(record):
                return color
        return False

    def _repr_html_(self):
        """ HTML representation
        """
        theaders = u"".join((u"<th>%s</th>" % header for header in self.iheaders))
        help = u"Note, that You may use <i>.to_csv()</i> method of this table to export it to CSV format"
        table = (u"<div><div>{help}</div><table>"
                 u"<caption>{self.caption}</caption>"
                 u"<tr>{headers}</tr>"
                 u"%s</table>"
                 u"<div>").format(self=self,
                                  headers=theaders,
                                  help=help)
        trow = u"<tr>%s</tr>"
        throw = u'<tr style="background: %s">%s</tr>'
        data = u""
        for record in self.irecords:
            hcolor = record['color']
            tdata = u"".join((u"<td>%s</td>" % fval for fval in record['row']))
            if hcolor:
                data += throw % (hcolor, tdata)
            else:
                data += trow % tdata
        return table % data

    def to_csv(self):
        """ Write table to CSV file and return FileLink object for it

            :return: instance of FileLink
            :rtype: FileLink
        """
        # Python 2/3 compatability
        if six.PY3:
            adapt = lambda s: s
            fmode = 'wt'
        else:
            fmode = 'wb'
            adapt = lambda s: s.encode('utf-8')

        tmp_file = tempfile.NamedTemporaryFile(mode=fmode, dir=CSV_PATH, suffix='.csv', delete=False)
        with tmp_file as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(tuple((adapt(h) for h in self.iheaders)))
            for record in self.irecords:
                csv_writer.writerow(tuple((adapt(r) for r in record['row'])))
        return FileLink(os.path.join(CSV_PATH, os.path.split(tmp_file.name)[-1]))

