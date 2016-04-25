import csv

from django.http import HttpResponse

class CSVResponse(HttpResponse):
    def __init__(self, filename):
        super(CSVResponse, self).__init__(content_type='text/csv; charset=UTF-8')
        self['Content-Disposition'] = 'attachment; filename="%s"' % filename.replace('"', r'\"')
        self.spreadsheet = csv.writer(self)

    def writerow(self, row):
        self.spreadsheet.writerow([unicode(r).encode('utf8') for r in row])
