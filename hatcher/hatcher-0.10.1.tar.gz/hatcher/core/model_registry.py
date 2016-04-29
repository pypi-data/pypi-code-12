from functools import wraps
import re

from .v0.organization import Organization as OrganizationV0
from .v0.repository import (
    Repository as RepositoryV0,
    SinglePlatformRepository as SinglePlatformRepositoryV0,
)
from .v0.team import Team as TeamV0
from .v0.user import User as UserV0
from .v1.repository import (
    Repository as RepositoryV1,
    SinglePlatformRepository as SinglePlatformRepositoryV1,
)


class InvalidApiVersion(Exception):
    pass


class InvalidApiVersionDefinition(Exception):
    pass


MODEL_VERSION_REGISTRY = '__model_versions__'


def is_model_factory(func):
    return callable(func) and hasattr(func, MODEL_VERSION_REGISTRY)


def versioned_model(**versions):
    API_VERSION_RE = re.compile(r'^v(?P<api_version>\d+)$')

    if len(versions) == 0:
        raise RuntimeError('No API versions given!')

    model_versions = {}
    for key, model in versions.items():
        match = API_VERSION_RE.match(key)
        if match is None:
            raise InvalidApiVersionDefinition(
                'Bad API version: {!r}'.format(key))
        if not isinstance(model, type) or not issubclass(model, object):
            raise InvalidApiVersionDefinition(
                'Model {!r} ({!r}) is not a class'.format(key, model))
        model_versions[int(match.group('api_version'))] = model

    def decorator(fn):
        @wraps(fn)
        def wrapper(self, *args, **kwargs):
            model = self._get_model_class(wrapper)
            return model

        setattr(wrapper, MODEL_VERSION_REGISTRY, model_versions)

        return wrapper

    return decorator


class ModelRegistry(object):

    def __init__(self, api_version=None):
        max_api_version = self._max_api_version()
        if api_version is None:
            api_version = max_api_version
        elif api_version > max_api_version:
            raise InvalidApiVersion(api_version)

        self.api_version = api_version

    @classmethod
    def _max_api_version(cls):
        max_api_version = 0
        factories = (getattr(cls, name) for name in dir(cls)
                     if is_model_factory(getattr(cls, name)))
        for factory in factories:
            versions = getattr(factory, MODEL_VERSION_REGISTRY)
            max_api_version = max(max_api_version, max(versions.keys()))
        return max_api_version

    def _get_model_class(self, wrapper):
        models = getattr(wrapper, MODEL_VERSION_REGISTRY)
        api_version = self.api_version

        model = models.get(api_version)
        if model is None:
            min_version = min(models.keys())
            if api_version < min_version:
                raise InvalidApiVersion(api_version)

            for version in sorted(models.keys(), reverse=True):
                if version < api_version:
                    model = models[version]
                    break

        return model

    @property
    def Organization(self):
        return self._Organization()

    @versioned_model(v0=OrganizationV0)
    def _Organization(self):
        pass

    @property
    def Repository(self):
        return self._Repository()

    @versioned_model(v0=RepositoryV0,
                     v1=RepositoryV1)
    def _Repository(self):
        pass

    @property
    def Team(self):
        return self._Team()

    @versioned_model(v0=TeamV0)
    def _Team(self):
        pass

    @property
    def User(self):
        return self._User()

    @versioned_model(v0=UserV0)
    def _User(self):
        pass

    @property
    def SinglePlatformRepository(self):
        return self._SinglePlatformRepository()

    @versioned_model(v0=SinglePlatformRepositoryV0,
                     v1=SinglePlatformRepositoryV1)
    def _SinglePlatformRepository(self):
        pass


MAX_API_VERSION = ModelRegistry._max_api_version()
