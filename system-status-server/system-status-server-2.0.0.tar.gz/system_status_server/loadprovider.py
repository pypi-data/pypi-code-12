
import os

from .dataproviderbase import DataProviderBase

class LoadProvider(DataProviderBase):

    def fetch(self):

        return dict(
            load = os.getloadavg()
        )
