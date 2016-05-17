import pandas as pd

from commons.registry import Registry


data_storers = Registry()


class DataStorerBase(object):
    """
    Base class for data storers.
    """

    def __call__(self, data):
        """
        Take a data frame and store it somewhere.
        """
        assert isinstance(data, pd.DataFrame)


@data_storers.register('csv')
class CSVFileStorer(DataStorerBase):
    def __init__(self, path, **kwargs):
        super(CSVFileStorer, self).__init__()
        self.path = path
        self.kwargs = kwargs

    def __call__(self, data):
        super(CSVFileStorer, self).__call__(data)
        data.to_csv(self.path, **self.kwargs)