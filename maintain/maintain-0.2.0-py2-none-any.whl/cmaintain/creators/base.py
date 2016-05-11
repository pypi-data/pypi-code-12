class ValidationError(Exception):
    pass


class Creator(object):
    name = 'unknown'
    available = True

    @classmethod
    def dependencies(cls):
        """
        Returns any other creators that are dependencies.
        """
        return []

    @classmethod
    def after(cls):
        """
        Returns any other creators that should be run beforehand.
        """
        return []

    def __init__(self, config, destination, creators=None):
        self.config = config
        self.destination = destination
        self.creators = creators or []

    def __str__(self):
        return self.name

    def validate(self):
        pass

    def pre_create(self):
        pass

    def create(self):
        raise NotImplementedError

    def post_create(self):
        pass

    #

    def find_creator(self, cls):
        return filter(lambda creator: isinstance(creator, cls), self.creators).pop()

