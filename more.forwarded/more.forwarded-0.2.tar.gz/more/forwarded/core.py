import morepath
from .forwarded import handler_factory


class ForwardedApp(morepath.App):
    pass


@ForwardedApp.tween_factory(over=morepath.HOST_HEADER_PROTECTION)
def forwarded_tween_factory(app, handler):
    return handler_factory(handler)
