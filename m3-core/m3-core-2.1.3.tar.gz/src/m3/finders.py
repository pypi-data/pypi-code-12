# -*- coding: utf-8 -*-
"""
Static files finders
"""
import os
from collections import OrderedDict

from django.apps import apps
from django.contrib.staticfiles.finders import AppDirectoriesFinder, BaseFinder
from django.core.files.storage import FileSystemStorage


class RecursiveAppDirectoriesFinder(AppDirectoriesFinder):
    """
    Поисковик файлов статики в подпапках приложений.
    Ищет в приложениях подпапки, содержащие папку static,
    но при этом не зарегистрированный, как приложения.
    Такие папки не подхватываются AppDirectoriesFinder'ом,
    но при этом для декомпозиции бывает полезно
    разнести статику внутри приложения

    ВАЖНО! Прописывать в settings его нужно после
    'django.contrib.staticfiles.finders.AppDirectoriesFinder'
    """
    storage_class = FileSystemStorage

    def __init__(self, app_names=None, *args, **kwargs):
        self.apps = []
        self.storages = OrderedDict()
        visited = set()

        def traverse(path, root=False):
            for sub in os.listdir(path):
                full_path = os.path.abspath(os.path.join(path, sub))
                if full_path not in visited and os.path.isdir(full_path):
                    if sub == 'static' and not root:
                        storage = self.storage_class(full_path)
                        storage.prefix = None  # Иначе не работает
                        self.apps.append(full_path)
                        self.storages[full_path] = storage
                    else:
                        traverse(full_path)

        for app_config in apps.get_app_configs():
            traverse(app_config.path, root=True)

        # пропускаем __init__ предка, ибо не поведение переопределено
        BaseFinder.__init__(self, *args, **kwargs)
