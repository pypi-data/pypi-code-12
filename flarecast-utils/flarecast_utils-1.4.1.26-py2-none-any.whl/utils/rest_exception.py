__author__ = 'cansik'


class RestException(Exception):
    def __init__(self, request, message=''):
        self.request = request
        self.message = message

    def __str__(self):
        if self.message != '':
            return "%s | %s " % (self.message, self.request.text)
        return "%s" % self.request.text
