import pandas as pd
import os
import time

from commons.registry import Registry


data_sources = Registry()


class DataProviderBase(object):
    """
    Base class for data providers.
    """

    def __call__(self):
        """
        Load data into data frame and return it.
        """
        raise NotImplementedError()


class CachingDataProviderBase(DataProviderBase):
    def __init__(self, use_cache=True):
        super(CachingDataProviderBase, self).__init__()
        self.value = None
        self.use_cache = use_cache

    def __call__(self):
        if self.use_cache:
            if self.value is None:
                self.value = self._load()
                assert self.value is not None, 'Can not load data'
            return self.value
        else:
            return self._load()

    def _load(self):
        raise NotImplementedError()


@data_sources.register('csv')
class CSVDataProvider(CachingDataProviderBase):
    def __init__(self, path, sep='\t', use_cache=True, **kwargs):
        super(CSVDataProvider, self).__init__(use_cache)
        self.path = path
        self.sep = sep
        self.kwargs = kwargs

    def _load(self):
        return pd.read_csv(self.path, sep=self.sep, **self.kwargs)


@data_sources.register('sql')
class SQLDataProvider(CachingDataProviderBase):
    def __init__(self, sql, connection, use_cache=True, file_cache=None, file_cache_expiry=None, retries=1, **kwargs):
        super(SQLDataProvider, self).__init__(use_cache)
        self.file_cache_expiry = file_cache_expiry
        self.file_cache = file_cache
        self.sql = sql
        self.kwargs = kwargs
        self.retries = retries
        self.connection_str = connection

    @property
    def connection(self):
        try:
            from sqlalchemy import create_engine
        except:
            raise ImportError('SQL data provider requires sqlalchemy')
        return create_engine(self.connection_str)

    def _load(self):
        if not self.file_cache:
            return self._load_sql()
        else:
            return self._check_cache_and_load()

    def _check_cache_and_load(self):
        if os.path.exists(self.file_cache) and (
            self.file_cache_expiry is None or time.time() - os.path.getmtime(self.file_cache) < self.file_cache_expiry
        ):
            return self._load_from_cache()
        data = self._load_sql()
        self._update_cache(data)
        return data

    def _update_cache(self, data):
        try:
            os.makedirs(os.path.dirname(self.file_cache))
        except OSError:
            pass  # exists_ok is unavailable in 2.7
        data.to_csv(self.file_cache, sep='\t', index=False, header=True)

    def _load_from_cache(self):
        return pd.read_csv(self.file_cache, sep='\t')

    def _load_sql(self):
        err = None
        for i in range(self.retries):
            try:
                return pd.read_sql(self.sql, self.connection, **self.kwargs)
            except BaseException as e:
                err = e
        raise err


@data_sources.register('blaze')
class BlazeDataProvider(CachingDataProviderBase):
    def __init__(self, uri, expr=None, use_cache=False):
        super(BlazeDataProvider, self).__init__(use_cache)
        self.uri = uri
        self.expr = expr

    def _load(self):
        import blaze as bl
        _ = bl.Data(self.uri)
        if self.expr:
            _ = eval(self.expr, globals(), locals())
        return bl.into(pd.DataFrame, _)
