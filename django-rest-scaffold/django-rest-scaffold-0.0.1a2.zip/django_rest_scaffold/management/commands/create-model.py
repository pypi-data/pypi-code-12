# -*- coding: UTF-8 -*-
"""
    Created by Régis Eduardo Crestani <regis.crestani@gmail.com> on 19/06/2016.
"""
import os

from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django_rest_scaffold.settings import DJANGO_REST_SCAFFOLD_SETTINGS as SETTINGS


class Command(BaseCommand):
    help = 'Creates a model, serializer and views'

    def add_arguments(self, parser):
        parser.add_argument('model-name', type=str)
        parser.add_argument('resource-name', type=str)
        parser.add_argument('file-mode', nargs='?', type=str)

    @staticmethod
    def gen_header() -> list:
        today = datetime.now().strftime('%d/%m/%Y')
        return [
            '# -*- coding: UTF-8 -*-\n',
            '"""\n',
            '    Created by Régis Eduardo Crestani <regis.crestani@gmail.com> on %s.\n' % today,
            '"""\n'
        ]

    @staticmethod
    def build_comment(model_name: str, text: str) -> str:
        line = '# {0}\n'.format('-' * 118)
        return '{0}#    {1} {2}\n{0}'.format(line, model_name.upper(), text.upper())

    def handle(self, *args, **options):
        model_name = options.get('model-name')
        resource_name = options.get('resource-name')
        file_mode = options.get('file-mode', None) or 'a+'
        model_name_slug = ''.join([v if p == 0 or v.islower() else '-' + v for p, v in enumerate(model_name)]).lower()

        serializer_name = '%sSerializer' % model_name
        view_resource_name = '%sResourceAPIView' % model_name
        view_detail_name = '%sDetailAPIView' % model_name

        resource_path = os.path.join(SETTINGS['APPS_FOLDER'], resource_name)
        apps_folder_name = SETTINGS['APPS_FOLDER_NAME']
        apps_folder_package = '' if apps_folder_name is None else '{0}.'.format(apps_folder_name)
        if not os.path.exists(resource_path):
            CommandError('Resource %s not found.' % resource_name)

        # CREATE THE MODELS FILE
        models_path = os.path.join(resource_path, 'models.py')
        if not os.path.exists(models_path) or 'w' in file_mode:
            models_lines = Command.gen_header()
            models_lines.append('from django.db import models\n')
        else:
            models_lines = []
        models_lines += [
            '\n\n',
            'class {0}(models.Model):\n'.format(model_name),
            '    pass\n'
        ]
        with open(models_path, file_mode, encoding='utf-8') as models_file:
            models_file.writelines(models_lines)

        # CREATE THE SERIALIZERS FILE
        serializers_path = os.path.join(resource_path, 'serializers.py')
        if not os.path.exists(serializers_path) or 'w' in file_mode:
            serializers_lines = Command.gen_header()
            serializers_lines.append('from rest_framework import serializers')
        else:
            serializers_lines = []
        serializers_lines += [
            '\n\n',
            Command.build_comment(model_name_slug, 'serializers'),
            'from {0}{1}.models import {2}\n'.format(apps_folder_package, resource_name, model_name),
            '\n\n',
            'class {0}(serializers.ModelSerializer):\n'.format(serializer_name),
            '    class Meta:\n',
            '        model = {0}\n'.format(model_name)
        ]
        with open(serializers_path, file_mode, encoding='utf-8') as serializers_file:
            serializers_file.writelines(serializers_lines)

        # CREATE THE VIEWS FILE
        views_path = os.path.join(resource_path, 'views.py')
        if not os.path.exists(views_path) or 'w' in file_mode:
            views_lines = Command.gen_header()
            views_lines.append('from rest_framework import generics')
        else:
            views_lines = []
        views_lines += [
            '\n\n',
            Command.build_comment(model_name_slug, 'views'),
            'from {0}{1}.models import {2}\n'.format(apps_folder_package, resource_name, model_name),
            'from {0}{1}.serializers import {2}\n'.format(apps_folder_package, resource_name, serializer_name),
            '\n\n',
            'class {0}(generics.ListCreateAPIView):\n'.format(view_resource_name),
            '    serializer_class = {0}\n'.format(serializer_name),
            '    queryset = {0}.objects\n'.format(model_name),
            '\n\n',
            'class {0}(generics.RetrieveUpdateDestroyAPIView):\n'.format(view_detail_name),
            '    serializer_class = {0}\n'.format(serializer_name),
            '    queryset = {0}.objects\n'.format(model_name),
        ]
        with open(views_path, file_mode, encoding='utf-8') as views_file:
            views_file.writelines(views_lines)

        # CREATE THE URLS FILE
        urls_path = os.path.join(resource_path, 'urls.py')
        if not os.path.exists(urls_path) or 'w' in file_mode:
            urls_lines = Command.gen_header()
            urls_lines += [
                'from django.conf.urls import url\n',
                '\n',
                'urlpatterns = []\n'
            ]
        else:
            urls_lines = []
        urls_lines += [
            '\n',
            Command.build_comment(model_name_slug, 'endpoints'),
            'from {0}{1}.views import {2}, {3}\n'.format(apps_folder_package, resource_name, view_resource_name,
                                                         view_detail_name),
            '\n',
            'urlpatterns += [\n',
            "    url(r'^{0}s/$', {1}.as_view(), name='{0}-resource'),\n".format(model_name_slug, view_resource_name),
            "    url(r'^{0}s/(?P<pk>\d+)[/]?$', {1}.as_view(), name='{0}-detail')\n".format(model_name_slug,
                                                                                            view_detail_name),
            ']\n'
        ]
        with open(urls_path, file_mode, encoding='utf-8') as urls_file:
            urls_file.writelines(urls_lines)

        # CREATE THE ADMIN FILE
        admin_path = os.path.join(resource_path, 'admin.py')
        if not os.path.exists(admin_path) or 'w' in file_mode:
            admin_lines = Command.gen_header()
            admin_lines.append('from django.contrib import admin')
        else:
            admin_lines = []
        admin_lines += [
            '\n\n',
            Command.build_comment(model_name_slug, 'admin register'),
            'from {0}{1}.models import {2}\n'.format(apps_folder_package, resource_name, model_name),
            '\n',
            'admin.site.register({0})\n'.format(model_name),
        ]
        with open(admin_path, file_mode, encoding='utf-8') as admin_file:
            admin_file.writelines(admin_lines)
