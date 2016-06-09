# coding: utf-8
import os
import datetime
from django.conf import settings
from django.db import models

__author__ = 'damirazo <me@damirazo.ru>'


class CreadocReport(models.Model):
    u"""
    Модель шаблона отчетной формы
    """
    guid = models.CharField(
        max_length=128,
        unique=True,
        verbose_name=u'Уникальный идентификатор шаблона')
    name = models.CharField(
        max_length=128,
        verbose_name=u'Наименование шаблона')
    author = models.ForeignKey(
        to='auth.User',
        verbose_name=u'Автор шаблона', null=True)
    created_at = models.DateTimeField(
        auto_now_add=True,
        default=datetime.datetime.now,
        verbose_name=u'Дата и время создания записи')
    changed_at = models.DateTimeField(
        auto_now=True,
        default=datetime.datetime.now,
        verbose_name=u'Дата и время последнего изменения')
    state = models.BooleanField(default=True, verbose_name=u'Статус шаблона')

    @property
    def path(self):
        u"""
        Путь до файла с шаблоном
        """
        return os.path.join(settings.CREADOC_REPORTS_ROOT, self.guid + '.mrt')

    @property
    def url(self):
        u"""
        url, по которому доступен файл с шаблоном для скачивания
        """
        return '{}{}/{}.mrt'.format(
            settings.MEDIA_URL,
            settings.CREADOC_REPORTS_DIR,
            self.guid)

    class Meta:
        db_table = 'creadoc_report'
        verbose_name = u'Шаблон отчетной формы'
        verbose_name_plural = u'Шаблоны отчетных форм'


class CreadocReportDataSource(models.Model):
    u"""
    Подключенный к шаблону источник данных
    """
    report = models.ForeignKey(
        to='CreadocReport', verbose_name=u'Отчетная форма')
    source_uid = models.CharField(
        max_length=128, verbose_name=u'Идентификатор источника данных')

    class Meta:
        db_table = 'creadoc_report_data_source'
        verbose_name = u'Подключенный источник данных'
        verbose_name_plural = u'Подключенные источники данных'
