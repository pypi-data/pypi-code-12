# coding: utf-8
from copy import copy
from m3.actions import urls

__author__ = 'damirazo <me@damirazo.ru>'


def redirect_to_action(request, action, params=None):
    u"""
    Перенаправление запроса в другой экшен
    :param request: WSGIRequest
    :param action: Экземпляр класса экшена
    :param params: Словарь с набором параметров,
        которые будут переданы с запросом в указанный экшен
    :rtype: Response
    """
    controller = action.controller
    request.path = urls.get_url(action)
    new_post = copy(request.POST)

    if params:
        new_post.update(params)

    request.POST = new_post

    # Совместимость с django 1.4-
    if hasattr(request, '_request'):
        del request._request

    return controller.process_request(request)
