from collections import deque


class Store(object):
    """In-memory storage of recent data. A global instance is
    available as ``brush.stores.store``.

    :param int maxlen: Maximum number of points to store

    """
    def __init__(self, maxlen=60):
        assert maxlen > 0
        assert isinstance(maxlen, int)
        self._data = None
        self._keys = None
        self._metadata = dict()
        self.maxlen = maxlen
        self.clear()
        self.callback = None

    def __getitem__(self, idx):
        return self._data[idx]

    def __iter__(self):
        return self._data.__iter__()

    def __str__(self):
        return str(self._data)

    def __repr__(self):
        return str(self._data)

    def keys(self, recache=False):
        if self._keys is None or recache:
            self._keys = sorted(list(self._data[0].keys()))
        return self._keys

    @property
    def maxlen(self):
        return self._maxlen

    @maxlen.setter
    def maxlen(self, length):
        self._maxlen = length
        try:
            data = self._data.copy()
        except:
            pass
        self._data = deque(maxlen=self._maxlen)
        try:
            self._data.extend(data)
        except:
            pass

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, data):
        meta = {
            key.replace('.', '_'): data[key] for key in data
        }
        self._metadata = meta

    def append(self, data):
        """Append data to the store. The oldest data item will be
        removed if appending results in exceeding the maximum
        length.

        :param dict data:

        """
        assert isinstance(data, dict)
        self._data.appendleft(data.copy())
        if self.callback is not None:
            self.callback(data)

    def clear(self):
        self._data = deque(maxlen=self.maxlen)

    def get(self, amount=1):
        """Access data from the store.

        :param int amount: maximum number of data items to return or -1
                           to get all

        """
        assert amount >= 1 or amount == -1
        if amount == 1:
            return self._data[0]
        else:
            if amount == -1:
                stop = len(self._data)
            else:
                stop = amount
            result = dict()
            for i in range(stop):
                data = self._data[i]
                for key in data:
                    if key not in result:
                        result[key] = [data[key]]
                    else:
                        result[key].append(data[key])
            return result


store = Store()
