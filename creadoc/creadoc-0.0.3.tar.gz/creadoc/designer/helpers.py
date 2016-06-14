# coding: utf-8
import os
import uuid
import tempfile
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


def get_tmp_file_path(file_name=None):
    u"""
    Создает временный файл во к каталоге временных файлов.
    Использовать tempfile в проекте не надо,
    работаем через этот метод api.

    :param str or None: имя файла, если не задано то будет
        само сгенерировано
    :rtype unicode:
    """
    if not file_name or not isinstance(file_name, basestring):
        file_name = '{}.tmp'.format(uuid.uuid4().get_hex())

    return os.path.realpath(
        os.path.join(tempfile.gettempdir(), file_name))
