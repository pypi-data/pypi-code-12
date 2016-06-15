# coding: utf-8
import os
import json
import uuid
import tempfile
from copy import copy
from zipfile import ZipFile
from django.conf import settings
from m3.actions import urls, ApplicationLogicException
from creadoc.designer.exceptions import SkipTemplateException
from creadoc.report.registry import CR
from creadoc.models import CreadocReport, CreadocReportDataSource

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


def load_template(template_path, user=None, overwrite=False):
    u"""
    Загрузка шаблона в формате creadoc в систему

    :param template_path: Путь до шаблона или файловый дескриптор
    :param user: Объект пользователя, который будет указан как автор шаблона.
        По умолчанию - пусто.
    :param overwrite: Признак необходимости перезаписи существующего шаблона.
        В противном случае шаблон будет пропущен.
    """
    zip_file = ZipFile(template_path)

    # Получение мета-данных
    with open(zip_file.extract('META.json', get_tmp_file_path()), 'r') as file_meta:  # noqa
        meta_data = json.loads(file_meta.read())

    if meta_data is None:
        raise ApplicationLogicException(
            u'Не удалось получить информацию о шаблоне. '
            u'Возможно файл поврежден.')

    report_guid = meta_data['guid']
    report_name = meta_data['name']

    # Если шаблон есть и при этом не стоит признак перезаписи, то пропускаем его
    if CreadocReport.objects.filter(guid=report_guid).exists() and not overwrite:  # noqa
        raise SkipTemplateException
    # Если указан признак перезаписи, то удаляем существующие записи
    elif overwrite:
        try:
            existed_report = CreadocReport.objects.get(guid=report_guid)
        except CreadocReport.DoesNotExist:
            pass
        else:
            CreadocReportDataSource.objects.filter(
                report=existed_report
            ).delete()

            existed_report.delete()

    # Получение списка подключенных источников
    with open(zip_file.extract('sources.json', get_tmp_file_path()), 'r') as file_sources:  # noqa
        sources = json.loads(file_sources.read())

    template_name = '{}.mrt'.format(report_guid)
    template_path = os.path.join(
        settings.CREADOC_REPORTS_ROOT,
        template_name)

    # Сохраняем шаблон в общей директории шаблонов
    with open(zip_file.extract('report.json', get_tmp_file_path()), 'r') as file_template:  # noqa
        with open(template_path, 'w+') as dest_template:
            dest_template.write(file_template.read())

    report = CreadocReport()
    report.guid = report_guid
    report.name = report_name

    if user is not None and not user.is_anonymous():
        report.author = user

    report.save()

    for source_uid in sources:
        if CR.source(source_uid) is None:
            raise ApplicationLogicException((
                u'Не удалось подключить источник данных '
                u'с идентификатором {}. '
                u'Источник данных отсутствует.'
            ).format(source_uid))

        source = CreadocReportDataSource()
        source.report = report
        source.source_uid = source_uid
        source.save()
