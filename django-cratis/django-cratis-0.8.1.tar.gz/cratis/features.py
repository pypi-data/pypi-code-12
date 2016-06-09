import inspect
import os
import copy
from django.conf.urls import url
from django.utils.log import DEFAULT_LOGGING


from cratis.settings import CratisApplication
from cratis.settings import CratisConfig
from cratis.settings import FeatureNotLoadedYet
from cratis.utils import Collectable


class FeatureDependencyFailure(Exception):
    pass


class BaseFeature(object):
    calee = None
    """
    When future is used by other features using `with feature()` syntax,
    this variable get filled with reference to calee.
    """

    """
    Basement for all the features.
    """
    settings = None  # type: CratisConfig
    app = None  # type: CratisApplication

    _static_requirements = ()

    def __init__(self):
        super().__init__()

        self.__requirements = []

    def set_application(self, app):
        """
        Initialized just before configuration process start
        """
        self.app = app
        self.settings = app.scope

    def get_required(self):
        """
        Returns list of classes of features that must be loaded before this feature
        can be loaded
        """
        return self.__requirements

    def require_if_installed(self):
        return self.require(optional=True)

    def require(self, feature_cls, optional=False):
        try:
            _feature = self.app.get(feature_cls)
            _feature.calee = self
            yield _feature
            _feature.calee = None
        except (FeatureNotLoadedYet, ImportError) as e:
            if not optional:
                raise Exception('by %s' % self, e)

    def get_deps(self):
        """
        Return list of python dependencies that are required by the feature
        :return:
        """
        return ()

    def on_load(self, loaded_features):
        """
        Loads feature. Used by settings class.
        By default, checks requirements and executes configure_settings() method.

        As an argument accepts list of features loaded before current one.
        """

        self.configure_settings()

    def on_after_load(self):
        """
        Called when setting is configured
        """
        pass

    def on_startup(self):
        """
        Last chance to do something after settings are configured, called even later than on_after_load.
        """
        pass

    def configure_settings(self):
        """
        API method.
        Meant to be overridden by subsequent Features.

        Called inside on_load callback.
        """
        self.init()

    def init(self):
        """
        API method.
        Meant to be overridden by subsequent Features.

        Called inside on_load callback.
        """
        pass

    def configure_urls(self, urls):
        """
        API method.
        Meant to be overridden by subsequent Features.

        Called when django imports cratis.url from cratis.urls module.

        As a parameter accepts urlpatterns variable from cratis.urls
        """


def require(*features):
    def require_decorator(cls):
        cls.get_required = lambda x: features
        return cls

    return require_decorator


class Feature(BaseFeature):
    """
    Feature add some concreate functionality to the BaseFeature class.
    """

    # INSTALLED_APPS = Collectable()
    # MIDDLEWARE_CLASSES = Collectable()
    # TEMPLATE_CONTEXT_PROCESSORS = Collectable()
    # TEMPLATE_DIRS = Collectable()
    # STATICFILES_DIRS = Collectable()

    def get_dir(self):
        return os.path.dirname(inspect.getfile(self.__class__))

    def set_default(self, name, value):

        if not hasattr(self.settings, name):
            setattr(self.settings, name, value)

    def append_apps(self, apps):
        """
        Use this in configure_settings, to append new INSTALLED_APPS.
        """

        if isinstance(apps, str):
            apps = (apps,)

        if not hasattr(self.settings, 'INSTALLED_APPS'):
            self.settings.INSTALLED_APPS = ()

        for app in apps:
            if app not in self.settings.INSTALLED_APPS:
                self.settings.INSTALLED_APPS += (app,)

    def append_middleware(self, classes):
        """
        Use this in configure_settings, to append new middleware classes.
        """

        if isinstance(classes, str):
            classes = (classes,)

        if not hasattr(self.settings, 'MIDDLEWARE_CLASSES'):
            self.settings.MIDDLEWARE_CLASSES = ()

        for classname in classes:
            if classname not in self.settings.MIDDLEWARE_CLASSES:
                self.settings.MIDDLEWARE_CLASSES += (classname,)

    def append_template_processor(self, processors):
        """
        Use this in configure_settings, to append new template processors.
        """
        if isinstance(processors, str):
            processors = (processors,)

        if not hasattr(self.settings, 'TEMPLATE_CONTEXT_PROCESSORS'):
            self.settings.TEMPLATE_CONTEXT_PROCESSORS = ()

        for classname in processors:
            if classname not in self.settings.TEMPLATE_CONTEXT_PROCESSORS:
                self.settings.TEMPLATE_CONTEXT_PROCESSORS += (classname,)

    def append_template_dir(self, dirs):

        if isinstance(dirs, str):
            dirs = (dirs,)

        if not hasattr(self.settings, 'TEMPLATE_DIRS'):
            self.settings.TEMPLATE_DIRS = ()

        self.settings.TEMPLATE_DIRS += tuple(dirs)

    def append_asset_dir(self, dirs):
        if isinstance(dirs, str):
            dirs = (dirs,)

        if not hasattr(self.settings, 'STATICFILES_DIRS'):
            self.settings.STATICFILES_DIRS = ()

        self.settings.STATICFILES_DIRS += tuple(dirs)


class Common(Feature):
    """
    This feature is used by most of the django-applications
    """

    def __init__(self, sites_framework=True):
        super().__init__()

        self.sites_framework = sites_framework

    def configure_settings(self):
        s = self.settings

        self.append_apps([
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
        ])

        self.append_middleware([
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.locale.LocaleMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
        ])



        s.STATIC_URL = '/static/'
        s.STATIC_ROOT = s.BASE_DIR + '/var/static'

        s.MEDIA_URL = '/media/'
        s.MEDIA_ROOT = s.BASE_DIR + '/var/media'

        s.USE_TZ = True

        self.append_asset_dir(
            s.BASE_DIR + '/assets',
        )

        self.append_template_dir(
             s.BASE_DIR + '/templates/',
        )

        if self.sites_framework:
            self.append_apps([
                'django.contrib.sites',
            ])
            s.SITE_ID = 1

        s.LOGGING = copy.deepcopy(DEFAULT_LOGGING)

    def configure_urls(self, urls):
        if self.settings.DEBUG:
            from django.views.static import serve
            urls += [
                url(r'^media/(?P<path>.*)$', serve, {'document_root': self.settings.MEDIA_ROOT}),
                url(r'^static/(?P<path>.*)$', serve, {'document_root': self.settings.STATIC_ROOT}),
            ]
