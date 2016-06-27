"""Helpers around Pyramid "view_config" decorators for the REST API.
"""

from pyramid.view import view_config


def _merge_settings(settings, default_settings):
    default_settings.update({
        'http_cache': 0,
        'renderer': 'json',
    })
    default_settings.update(settings)
    return default_settings


class list(view_config):
    def __init__(self, model, **settings):
        super(list, self).__init__(**_merge_settings(settings, {
            'permission': 'read',
            'route_name': '%s_list' % model,
        }))


class create(view_config):
    def __init__(self, model, **settings):
        super(create, self).__init__(**_merge_settings(settings, {
            'permission': 'create',
            'route_name': '%s_create' % model,
        }))


class read(view_config):
    def __init__(self, model, **settings):
        super(read, self).__init__(**_merge_settings(settings, {
            'permission': 'read',
            'request_method': 'GET',
            'route_name': model,
        }))


class update(view_config):
    def __init__(self, model, **settings):
        super(update, self).__init__(**_merge_settings(settings, {
            'permission': 'update',
            'request_method': 'PUT',
            'route_name': model,
        }))


class patch(view_config):
    def __init__(self, model, **settings):
        super(patch, self).__init__(**_merge_settings(settings, {
            'permission': 'update',
            'request_method': 'PATCH',
            'route_name': model,
        }))


class delete(view_config):
    def __init__(self, model, **settings):
        super(delete, self).__init__(**_merge_settings(settings, {
            'permission': 'delete',
            'request_method': 'DELETE',
            'route_name': model,
        }))


class rel_list(view_config):
    def __init__(self, model, **settings):
        super(rel_list, self).__init__(**_merge_settings(settings, {
            'permission': 'read',
            'route_name': '%s_rel_list' % model,
        }))


class rel_create(view_config):
    def __init__(self, model, **settings):
        super(rel_create, self).__init__(**_merge_settings(settings, {
            'permission': 'update',
            'route_name': '%s_rel_create' % model,
        }))


class rel_add(view_config):
    def __init__(self, model, **settings):
        super(rel_add, self).__init__(**_merge_settings(settings, {
            'permission': 'update',
            'request_method': 'PUT',
            'route_name': '%s_rel' % model,
        }))


class rel_delete(view_config):
    def __init__(self, model, **settings):
        super(rel_delete, self).__init__(**_merge_settings(settings, {
            'permission': 'update',
            'request_method': 'DELETE',
            'route_name': '%s_rel' % model,
        }))
