

class CacheMixin(object):

    def __init__(self):
        pass

    def unique_id(self):
        raise NotImplementedError

    def get_last_modified(self):
        raise NotImplementedError

    def get_last_cached(self):
        raise NotImplementedError
