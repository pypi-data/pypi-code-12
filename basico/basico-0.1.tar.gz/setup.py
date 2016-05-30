#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Authors: Tomás Vírseda <tomasvirseda@gmail.com>
# Basico is a SAP Notes manager for SAP Consultants
# Copyright (C) 2016 Tomás Vírseda
#
# Basico is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Basico is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Basico.  If not, see <http://www.gnu.org/licenses/gpl.html>

import os
import subprocess
from setuptools import setup


with open('README') as f:
    long_description = f.read()

def add_data():
    try:
        data_files = [
            ('basico/share/applications', ['basico/data/desktop/basico.desktop']),
            ('basico/data/icons',
                [
                    'basico/data/icons/annotation.png',
                    'basico/data/icons/bookmark.png',
                    'basico/data/icons/browse.png',
                    'basico/data/icons/category.png',
                    'basico/data/icons/component.png',
                    'basico/data/icons/delete.png',
                    'basico/data/icons/noproject.png',
                    'basico/data/icons/project.png',
                    'basico/data/icons/sapnote.png',
                    'basico/data/icons/notask.png',
                    'basico/data/icons/task.png',
                    'basico/data/icons/tasks.png',
                ]),
            ('basico/data/ui', ['basico/data/ui/basico.ui']),
            ('basico/data/share', []),
            ("basico/data/share/docs",
                    [
                    'AUTHORS',
                    'LICENSE',
                    'README',
                    'INSTALL',
                    'CREDITS',
                    'Changelog'
                    ]),
            ]

        if not os.path.isdir('mo'):
            os.mkdir('mo')
        for pofile in os.listdir('po'):
            if pofile.endswith('po'):
                lang = pofile.strip('.po')
                modir = os.path.join('mo', lang)
                if not os.path.isdir(modir):
                    os.mkdir(modir)
                mofile = os.path.join(modir, 'basico.mo')
                subprocess.call('msgfmt {} -o {}'.format(os.path.join('po', pofile), mofile), shell=True)
                data_files.append(['share/locale/{}/LC_MESSAGES/'.format(lang), [mofile]])
        return data_files
    except:
        return []

if os.name == 'posix':
    data_files = add_data()
else:
    data_files = []

try:
    bcommit = subprocess.check_output("svn info", shell=True)
    ucommit = bcommit.decode(encoding='UTF-8')
    icommit = int(ucommit.split('\n')[6].split(':')[1])
    dcommit = ucommit.split('\n')[11][19:29]
except Exception as error:
    print (error)
    dcommit = 'None'
    icommit = 0

setup(
    name='basico',
    version='0.1',
    author='Tomás Vírseda',
    author_email='tomasvirseda@gmail.com',
    url='http://subversion.t00mlabs.net/basico',
    description='SAP Notes Manager for SAP Consultants',
    long_description=long_description,
    download_url = 'http://t00mlabs.net/downloads/basico-0.1.tar.gz',
    license='GPLv3',
    packages=['basico'],
    # distutils does not support install_requires, but pip needs it to be
    # able to automatically install dependencies
    install_requires=[
          'pygal',
          'python-dateutil',
          'selenium',
          'feedparser',
    ],
    include_package_data=True,
    data_files=data_files,
    zip_safe=False,
    platforms='any',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: X11 Applications :: Gnome',
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Other Audience',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Topic :: Database :: Front-Ends',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities'
    ],
    entry_points={
        #~ 'console_scripts': [
            #~ 'basico = basico:main',
            #~ ],
        'gui_scripts': [
            'basico = basico.basico:main',
            ]
        },
)
