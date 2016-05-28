from tek.errors import TException

class UnknownSeries(TException):
    def __init__(self, name, best, best_ratio):
        text = 'Unknown series "{}"! (Best match was {} with ratio {})'
        super(UnknownSeries, self).__init__(text.format(name, best, best_ratio))
