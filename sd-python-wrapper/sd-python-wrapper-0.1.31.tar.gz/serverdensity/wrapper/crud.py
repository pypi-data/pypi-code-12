from serverdensity import Response


class CRUD(object):

    api = None

    def create(self, data=None, **kwargs):
        if not data:
            data = self._data

        return self.__class__(self.api.post(url=self.PATHS['create'], data=data, **kwargs))

    def delete(self, _id=None, **kwargs):
        if not _id:
            _id = self._id
        return self.__class__(self.api.delete(url=self.PATHS['delete'].format(_id), **kwargs))

    def list(self, **kwargs):
        result = self.api.get(url=self.PATHS['list'], **kwargs)
        return [self.__class__(item) for item in result]

    def update(self, _id=None, data=None, **kwargs):
        if not _id and data:
            data = self._data
            _id = self._id

        return self.__class__(self.api.put(url=self.PATHS['update'].format(_id), data=data, **kwargs))

    def view(self, _id=None, **kwargs):
        if not _id:
            _id = self._id
        return self.__class__(self.api.get(url=self.PATHS['view'].format(_id), **kwargs))
