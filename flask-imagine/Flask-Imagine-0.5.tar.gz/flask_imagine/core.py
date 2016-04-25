"""
Flask Imagine extension.
"""
from __future__ import unicode_literals
import logging

from io import BytesIO
from flask import current_app, abort, redirect

from flask.ext.imagine.adapters import *
from flask.ext.imagine.filters import *

from .helpers.regex_route import RegexConverter

LOGGER = logging.getLogger(__file__)


class Imagine(object):
    """
    Flask Imagine extension
    """
    _adapters = {
        'fs': ImagineFilesystemAdapter
    }
    _filters = {
        'autorotate': AutorotateFilter,
        'crop': CropFilter,
        'downscale': DownscaleFilter,
        'relative_resize': RelativeResizeFilter,
        'rotate': RotateFilter,
        'thumbnail': ThumbnailFilter,
        'upscale': UpscaleFilter,
        'watermark': WatermarkFilter
    }

    _filter_sets = {}
    _adapter = None
    _redirect_code = 302

    def __init__(self, app=None):
        """
        :param app: Flask application
        """
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        :param app: Flask application
        """
        if not hasattr(app, 'extensions'):  # pragma: no cover
            app.extensions = {}
        app.extensions['imagine'] = self

        self._set_defaults(app)

        self._redirect_code = app.config['IMAGINE_CACHE_REDIRECT_CODE']

        if isinstance(app.config['IMAGINE_ADAPTERS'], dict):
            self._adapters.update(app.config['IMAGINE_ADAPTERS'])
        if isinstance(app.config['IMAGINE_FILTERS'], dict):
            self._filters.update(app.config['IMAGINE_FILTERS'])

        self._handle_adapter(app)
        self._handle_filter_sets(app)

        self._add_url_rule(app)

    @classmethod
    def _set_defaults(cls, app):
        """
        Set default configuration parameters
        :param app: Flask application
        :return: Flask application
        """
        app.config.setdefault('IMAGINE_URL', '/media/cache/resolve')
        app.config.setdefault('IMAGINE_NAME', 'imagine')
        app.config.setdefault('IMAGINE_CACHE_ENABLED', True)
        app.config.setdefault('IMAGINE_CACHE_REDIRECT_CODE', 302)

        app.config.setdefault('IMAGINE_ADAPTERS', {})
        app.config.setdefault('IMAGINE_FILTERS', {})

        app.config.setdefault('IMAGINE_ADAPTER', {
            'name': 'fs',
        })

        app.config.setdefault('IMAGINE_FILTER_SETS', {})

        return app

    def _handle_adapter(self, app):
        """
        Handle storage _adapter configuration
        :param app: Flask application
        """
        if 'IMAGINE_ADAPTER' in app.config \
                and 'name' in app.config['IMAGINE_ADAPTER'] \
                and app.config['IMAGINE_ADAPTER']['name'] in self._adapters.keys():
            self._adapter = self._adapters[app.config['IMAGINE_ADAPTER']['name']](
                **app.config['IMAGINE_ADAPTER']
            )
        else:
            raise ValueError('Unknown _adapter: %s' % str(app.config['IMAGINE_ADAPTER']))

    def _handle_filter_sets(self, app):
        """
        Handle filter sets
        :param app: Flask application
        """
        if 'IMAGINE_FILTER_SETS' in app.config and isinstance(app.config['IMAGINE_FILTER_SETS'], dict):
            for filter_name, filters_settings in app.config['IMAGINE_FILTER_SETS'].items():
                filter_set = []
                if isinstance(filters_settings, dict) and 'filters' in filters_settings:
                    for filter_type, filter_settings in filters_settings['filters'].items():
                        if filter_type in self._filters:
                            filter_item = self._filters[filter_type](**filter_settings)
                            if isinstance(filter_item, ImagineFilterInterface):
                                filter_set.append(filter_item)
                            else:
                                raise ValueError('Filter must be implement ImagineFilterInterface')
                        else:
                            raise ValueError('Unknown filter type: %s' % filter_type)

                    filter_config = {'filters': filter_set}
                    if 'cached' in filters_settings:
                        filter_config['cached'] = filters_settings['cached']
                    else:
                        filter_config['cached'] = app.config['IMAGINE_CACHE_ENABLED']

                    self._filter_sets.update({filter_name: filter_config})
                else:
                    raise ValueError('Wrong settings for filter: %s' % filter_name)
        else:
            raise ValueError('Filters configuration does not present')

    def _add_url_rule(self, app):
        """
        Add url rule for get filtered images
        :param app: Flask application
        :return: Flask application
        """
        app.url_map.converters['regex'] = RegexConverter
        app.add_url_rule(
            app.config['IMAGINE_URL'] + '/<regex("[^\/]+"):filter_name>/<path:path>',
            app.config['IMAGINE_NAME'],
            self.handle_request
        )

        return app

    def handle_request(self, filter_name, path):
        """
        Handle image request
        :param filter_name: filter_name
        :param path: image_path
        :return:
        """
        if filter_name in self._filter_sets:
            if self._filter_sets[filter_name]['cached']:
                cached_item_path = self._adapter.check_cached_item('%s/%s' % (filter_name, path))
                if cached_item_path:
                    return redirect(cached_item_path, self._redirect_code)

            resource = self._adapter.get_item(path)

            if resource:
                for filter_item in self._filter_sets[filter_name]['filters']:
                    resource = filter_item.apply(resource)

                if self._filter_sets[filter_name]['cached']:
                    return redirect(
                        self._adapter.create_cached_item('%s/%s' % (filter_name, path), resource),
                        self._redirect_code
                    )
                else:
                    output = BytesIO()
                    resource.save(output, format=str(resource.format))
                    return output.getvalue()
            else:
                LOGGER.warning('File "%s" not found.' % path)
                abort(404)
        else:
            LOGGER.warning('Filter "%s" not found.' % filter_name)
            abort(404)

    def clear_cache(self, path, filter_name=None):
        """
        Clear cache for resource path.
        :param path: str
        :param filter_name: str or None
        """
        if filter_name:
            self._adapter.remove_cached_item('%s/%s' % (filter_name, path))
        else:
            for filter_name in self._filter_sets:
                self._adapter.remove_cached_item('%s/%s' % (filter_name, path))

    def add_filter_set(self, filter_name, filter_set, cached=True):
        """
        Manual addition of filter set
        :param filter_name: str
        :param filter_set: list
        :param cached: bool
        """
        try:
            hash(filter_name)
        except TypeError as err:
            raise ValueError('Filter set name must be as instance of hashable type: %s' % str(err))

        if not isinstance(filter_set, list):
            raise ValueError('Filters must be a list.')

        if len(filter_set) == 0:
            raise ValueError('Filters count must be greater than 0.')

        for filter_instance in filter_set:
            if not isinstance(filter_instance, ImagineFilterInterface):
                raise ValueError('All filters must implement of ImagineFilterInterface.')

        if not isinstance(cached, bool):
            raise ValueError('Cached parameter must be a bool.')

        filter_config = {
            'filters': filter_set,
            'cached': cached
        }

        if filter_name not in self._filter_sets:
            self._filter_sets.update({filter_name: filter_config})
        else:
            raise ValueError('Duplicate filter set name.')

    def update_filter_set(self, filter_name, filter_set=None, cached=None):
        """
        Manual update of filter set
        :param filter_name: str
        :param filter_set: list
        :param cached: bool
        """
        try:
            hash(filter_name)
        except TypeError as err:
            raise ValueError('Filter set name must be as instance of hashable type: %s' % str(err))

        filter_config = self._filter_sets[filter_name]

        if filter_set is not None:
            if not isinstance(filter_set, list):
                raise ValueError('Filters must be a list.')

            if len(filter_set) == 0:
                raise ValueError('Filters count must be greater than 0.')

            for filter_instance in filter_set:
                if not isinstance(filter_instance, ImagineFilterInterface):
                    raise ValueError('All filters must implement of ImagineFilterInterface.')

            filter_config.update({'filters': filter_set})

        if cached is not None:
            if not isinstance(cached, bool):
                raise ValueError('Cached parameter must be a bool.')

            filter_config.update({'cached': cached})

        self._filter_sets.update({filter_name: filter_config})

    def remove_filter_set(self, filter_name):
        """
        Remove filter set by name
        :param filter_name: str
        """
        if filter_name in self._filter_sets:
            del self._filter_sets[filter_name]
        else:
            raise ValueError('Unknown filter set name.')


def imagine_cache_clear(path, filter_name=None):
    """
    Clear cache for resource path.
    :param path: str
    :param filter_name: str or None
    """
    self = current_app.extensions['imagine']
    self.clear_cache(path, filter_name)
