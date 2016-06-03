# -*- coding:utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
from .dependency import PackageDependency


def verify_dependency(requirements_path, disapprove_exit=False):
    """
    Validates package requirements.

    :param requirements_path: requirements textのpath
    :type requirements_path: string

    :param disapprove_exit: 問題時にexitするかどうかのフラグ
    :type disapprove_exit: bool
    """
    package_dependency = PackageDependency(disapprove_exit)
    package_dependency.verify(requirements_path)
    if package_dependency.import_requirements:
        for import_requirements_path in package_dependency.import_requirements:
            package_dependency.verify(import_requirements_path)
    package_dependency.result()
