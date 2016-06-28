#!/usr/bin/env python3
"""
Setup script for hackedit-python
"""
import os
from setuptools import setup, find_packages

import hackedit_python


# add build_ui command. This command is only used by developer to easily
# update the ui scripts.
# To use this command, you need to install the pyqt-distutils packages (using
# pip).
try:
    from pyqt_distutils.build_ui import build_ui
except ImportError:
    build_ui = None

# Babel commands for internationalisation and localisation
try:
    from babel.messages import frontend as babel
except ImportError:
    compile_catalog = None
    extract_messages = None
    init_catalog = None
    update_catalog = None
else:
    compile_catalog = babel.compile_catalog
    extract_messages = babel.extract_messages
    init_catalog = babel.init_catalog
    update_catalog = babel.update_catalog

# get long description
with open('README.rst', 'r') as readme:
    long_desc = readme.read()


data_files = []
# translations
translations = [
    ('share/locale/%s' % x[0].replace('data/locale/', ''),
     list(map(lambda y: x[0]+'/'+y, x[2])))
    for x in os.walk('data/locale/')
]
for dst, srclist in translations:
    checked_srclist = []
    for src in srclist:
        if src.endswith('.mo'):
            checked_srclist.append(src)
    if checked_srclist:
        data_files.append((dst, checked_srclist))

# run setup
setup(
    name='hackedit-python',
    version=hackedit_python.__version__,
    packages=find_packages(),
    include_package_data=True,
    keywords=['IDE', 'Intergrated Development Environment', 'TextEditor',
              'Editor'],
    url='https://github.com/HackEdit/hackedit-python',
    license='GPL',
    author='Colin Duquesnoy',
    author_email='colin.duquesnoy@gmail.com',
    description='A set of plugins that add Python support to HackEdit',
    long_description=long_desc,
    data_files=data_files,
    install_requires=['docutils'],
    entry_points={
        # our workspaces plugins (run script, rope,...)
        'hackedit.plugins.workspace_plugins': [
            'PyRun = hackedit_python.run:PyRun',
            'PyConsole = hackedit_python.pyconsole:PyConsole',
            'PyRefactor = hackedit_python.refactor:PyRefactor',
            'PyContextMenus = hackedit_python.context_menus:PyContextMenus',
            'PyOpenModule = hackedit_python.open_module:PyOpenModule',
            'PyCodeEditorIntegration = '
            'hackedit_python.editor:PyCodeEditorIntegration',
            'CleanPycFiles = hackedit_python.clean_pyc:CleanPycFiles'
        ],
        # custom preference page plugin for our python package manager
        'hackedit.plugins.preference_pages': [
            'interpreters = hackedit_python.interpreters:ManageInterpreters'
        ],
        'hackedit.plugins.symbol_parsers': [
            'PySymbolIndexor = hackedit_python.index:PySymbolParser'
        ],
        # builtin workspaces
        'hackedit.plugins.workspace_providers': [
            'python_workspace = hackedit_python.workspaces:PythonWorkspace'
        ],
        # templates
        'hackedit.plugins.template_providers': [
            'PyTemplatesProvider = '
            'hackedit_python.templates:PyTemplatesProvider'
        ],
        # pyqode.python editor integration
        'hackedit.plugins.editors': [
            'PyCodeEditorPlugin = hackedit_python.editor:PyCodeEditorPlugin',
        ],
    },
    cmdclass={
        'build_ui': build_ui,
        'compile_catalog': compile_catalog,
        'extract_messages': extract_messages,
        'init_catalog': init_catalog,
        'update_catalog': update_catalog
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: X11 Applications :: Qt',
        'Environment :: Win32 (MS Windows)',
        'Environment :: MacOS X',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development',
        'Topic :: Text Editors :: Integrated Development Environments (IDE)'
    ]
)
