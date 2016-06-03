# -*- coding:utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
from pkg_resources import get_distribution, yield_lines
from pkg_resources import VersionConflict, DistributionNotFound

import os
import re
from termcolor import colored

COLOR_WARNING = 'red'
COLOR_INFO = 'cyan'
COLOR_SUCCESS = 'green'
WARNING_NOT_FOUND = colored('NOT FOUND', COLOR_WARNING)
WARNING_VERSION_CONFLICT = colored('VERSION CONFLICT', COLOR_WARNING)
VERIFY_SUCCESS = colored('PKG VERIFY SUCCESS', COLOR_SUCCESS)
VERSION_MATCH_PATTERN = r"\s*(<=?|>=?|===?|!=|~=)"
REQUIREMENT_IMPORT_PATTERN = r"(?=.*-r)(?=.*txt)"
EGG_MATCH_PATTERN = r"#egg="


class PackageDependency(object):

    def __init__(self, disapprove_exit=False):
        self.import_requirements = []
        self.terminate = False
        self.disapprove_exit = disapprove_exit

    @staticmethod
    def requirements_exist(requirements_path=None):
        """
        requirements.txtの有無を確認する.

        :type requirements_path: string
        :rtype: string
        """
        if not requirements_path or not os.path.isfile(requirements_path):
            print(colored('{} not exists'.format(requirements_path), COLOR_WARNING))
            exit(1)
        return requirements_path

    @staticmethod
    def _get_import_path(import_file, requirements_path):
        """
        requirements.txt 分割の為のimportファイルの相対pathを生成

        :type import_file: string
        :rtype: string
        """
        dir_path = os.path.dirname(requirements_path)
        file_name = re.split(' ', import_file)[-1]
        return '{}/{}'.format(dir_path, file_name)

    @staticmethod
    def _data_split(package):
        """
        packageの内容を名前とバージョン指定とURL(gitの場合)等の情報を分解する.

        :type package: string
        :rtype: dict[string, string]
        """
        package_data = {'package': package,
                        'name': None,
                        'relation': None,
                        'version': 'any',
                        'source': None}
        if re.search(EGG_MATCH_PATTERN, package):
            p_list = re.split(EGG_MATCH_PATTERN, package)
            package_data['source'] = p_list[0]
            package_data['package'] = package_data['name'] = p_list[1]
        elif re.search(VERSION_MATCH_PATTERN, package):
            package_data['name'], package_data['relation'], package_data['version'] \
                = re.split(VERSION_MATCH_PATTERN, package)
        else:
            package_data['name'] = package
        return package_data

    def _check_import_file(self, import_file, requirements_path):
        """
        requirements.txt 分割の為のimport文かどうかの確認

        :type import_file: string
        :rtype: bool
        """
        if re.search(REQUIREMENT_IMPORT_PATTERN, import_file):
            import_path = self._get_import_path(import_file, requirements_path)
            if self.requirements_exist(import_path):
                self.import_requirements.append(import_path)
                return True
        return False

    def result(self):
        if not self.terminate:
            print("{comment}".format(comment=VERIFY_SUCCESS))

        if self.terminate and self.disapprove_exit:
            exit(1)

    def verify(self, requirements_path=None):
        """
        requirements.txtの内容と差異が無いか確認する.

        :type requirements_path: string
        :rtype: bool
        """
        self.requirements_exist(requirements_path)

        with open(requirements_path) as requirements:
            packages = yield_lines(requirements)
            for package in packages:
                if self._check_import_file(package, requirements_path):
                    continue
                package_data = self._data_split(package)
                try:
                    get_distribution(package_data['package'])
                except VersionConflict:
                    self.terminate = True
                    current_package = get_distribution(package_data['name'])
                    print("{comment}: {name}({before_ver}) => ({after_ver})".format(
                                                            comment=WARNING_VERSION_CONFLICT,
                                                            name=colored(package_data['name'], COLOR_INFO),
                                                            before_ver=colored(current_package.version, COLOR_INFO),
                                                            after_ver=colored(package_data['version'], COLOR_INFO)))
                except DistributionNotFound:
                    self.terminate = True
                    print("{comment}: {name}({ver})".format(
                                            comment=WARNING_NOT_FOUND,
                                            name=colored(package_data['name'], COLOR_INFO),
                                            ver=colored(package_data['version'], COLOR_INFO)))
        return self.terminate
