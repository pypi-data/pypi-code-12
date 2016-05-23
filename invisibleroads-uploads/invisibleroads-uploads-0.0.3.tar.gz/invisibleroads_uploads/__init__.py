from invisibleroads_posts import get_http_expiration_time

from .views import add_routes


def includeme(config):
    settings = config.registry.settings
    http_expiration_time = get_http_expiration_time(settings)

    config.add_static_view(
        '_/invisibleroads-uploads', 'invisibleroads-uploads:assets',
        cache_max_age=http_expiration_time)

    add_routes(config)
