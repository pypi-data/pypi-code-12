"""
Default settings for cratis project
"""
import os
from collections import OrderedDict
from typing import TypeVar

from cratis.utils import Resolvable
from django.utils.module_loading import import_string


class FeatureNotLoadedYet(Exception):
    pass


T = TypeVar('T')


class AttributeDictRef(object):

    data = None

    def __init__(self, data):
        super().__init__()
        self.data = data

    def __getattr__(self, name):
        try:
            return self.data[name]
        except KeyError:
            raise AttributeError

    def __setattr__(self, name, value):
        if not self.data:
            return super().__setattr__(name, value)
        self.data[name] = value


class CratisApplication(object):
    """
    App is intended to be used only for
    application introspecion needs.
    """

    def __init__(self, scope):
        super().__init__()

        self.scope = AttributeDictRef(scope)

        self.loaded_features = []
        self.features = []
        self.feature_map = {}

    def setup(self, env='Dev', var_name='CRATIS_APP'):
        self.scope.APP = self

        os.environ.setdefault(var_name, env)

        conf_class = self.scope.data[os.environ[var_name]]

        # Setup settings variables
        config = conf_class()
        props = {x: getattr(config, x) for x in dir(config) if not x.startswith('__')}
        self.scope.data.update(props)

        # prepare feature list to load
        feature_list = self.collect_features_with_deps(self.scope.FEATURES)

        for _feature in feature_list:
            self.load_feature(_feature)

        # resolve variable real values
        self.scope = {
            key: val.resolve() if isinstance(val, Resolvable) else val
            for (key, val) in self.scope.data.items()
        }

        for _feature in self.features:
            _feature.on_after_load()

        for _feature in self.features:
            _feature.on_startup()

    def load_feature(self, feature):
        feature.settings = self.scope
        feature.on_load(self.loaded_features)
        self.loaded_features.append(type(feature))
        self.features.append(feature)
        self.feature_map[feature.__class__] = feature

    def collect_features_with_deps(self, features):
        feature_map = OrderedDict()

        for feature in features:
            self.collect_feature_deps(feature, feature_map)

            # override
            feature_map[feature.__class__] = feature

        all_features = feature_map.values()
        return all_features

    def collect_feature_deps(self, feature, feature_map):
        for requirement in feature.get_required():
            if requirement.__class__ not in feature_map:
                self.collect_feature_deps(requirement, feature_map)
                feature_map[requirement.__class__] = requirement

    def get(self, feature_class: T) -> T:
        if isinstance(feature_class, str):
            feature_class = import_string(feature_class)

        try:
            return self.feature_map[feature_class]
        except KeyError:
            raise FeatureNotLoadedYet(
                'Feature %s is not yet loaded. Did you forget to add it as a requirement?' % feature_class)

    def is_loaded(self, feature_class):
        return feature_class in self.feature_map

    def find_features(self, interface):
        features = []
        for feature in self.features:
            if isinstance(feature, interface):
                features.append(feature)

        return features


class CratisConfig(object):
    """
    Base class for Configurations that will be used with cratis.

    Also class defines ROOT_URLCONF settings variable, that use cratis.urls
    to load all urls collected from your Features. Usually you wouldn't change this
    when working with cratis.

    BASE_DIR just points to project directory, so you can specify paths relatively, ex:
    """

    BASE_DIR = os.environ.get('CRATIS_APP_PATH', '.')
    ROOT_URLCONF = 'cratis.urls'

    FEATURES = ()


def override_feature(features, feature_to_override):
    """
    Replaces feature with the given one.

    :param feature_to_override:
    :return:
    """
    return tuple([x if not isinstance(x, type(feature_to_override)) else feature_to_override for x in features])


def skip_feature(features, feature):
    """
    Remove feature from feature list

    :param feature:
    :return:
    """
    return tuple([x for x in features if not isinstance(x, type(feature))])
