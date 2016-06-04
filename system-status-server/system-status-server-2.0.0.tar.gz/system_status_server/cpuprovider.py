
import psutil

from .dataproviderbase import DataProviderBase

class CPUProvider(DataProviderBase):

    def fetch(self):

        return dict(
            cpu = dict(
                cores = psutil.cpu_count()
            )
        )
