#!/usr/bin/env python3
"""
Setup script for HackEdit
"""
import os
import hackedit_cobol
from setuptools import setup, find_packages


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

print(data_files)

# run setup
setup(
    name='hackedit-cobol',
    version=hackedit_cobol.__version__,
    packages=[p for p in find_packages() if 'test' not in p],
    keywords=['IDE', 'Intergrated Development Environment', 'TextEditor',
              'Editor', 'COBOL', 'GnuCOBOL', 'OpenCOBOL', 'OpenCobolIDE'],
    url='https://github.com/HackEdit/hackedit-cobol',
    license='GPL',
    author='Colin Duquesnoy',
    author_email='colin.duquesnoy@gmail.com',
    description='A set of plugins that add COBOL support to HackEdit',
    long_description=long_desc,
    install_requires=['hackedit'],
    data_files=data_files,
    include_package_data=True,
    entry_points={
        # pyqode.cobol integration
        'hackedit.plugins.editors': [
            'CobolCodeEditPlugin = '
            'hackedit_cobol.plugins.editor:CobolCodeEditPlugin',
        ],
        # workspace plugins
        'hackedit.plugins.workspace_plugins': [
            'CobProjectManager = '
            'hackedit_cobol.plugins.project_mode:CobProjectManager',
            'CobFileManager = '
            'hackedit_cobol.plugins.file_mode:CobFileManager ',
            'CobOffsetCalculator = '
            'hackedit_cobol.plugins.offset:CobOffsetCalculator',
            'CobFileIndicators = '
            'hackedit_cobol.plugins.indicators:CobFileIndicators',
        ],
        # custom preference page plugin for the COBOL specific managers (
        # compilers, pre-parsers,...).
        'hackedit.plugins.preference_pages': [
            'CompilerPreferencesPlugin = hackedit_cobol.plugins.'
            'compiler_preferences:CompilerPreferencesPlugin',
            'PreparserPreferencesPlugin = hackedit_cobol.plugins.'
            'preparsers_preferences:PreparserPreferencesPlugin'
        ],
        # mimetype icon provider plugin
        'hackedit.plugins.file_icon_providers': [
            'CobolIconProvider = '
            'hackedit_cobol.plugins.icon_provider:CobolIconProvider'
        ],
        # plugin for indexing COBOL symbols
        'hackedit.plugins.symbol_parsers': [
            'CobSymbolIndexor = '
            'hackedit_cobol.plugins.index:CobolSymbolParser'
        ],
        # templates
        'hackedit.plugins.template_providers': [
            'CobTemplateProvider = '
            'hackedit_cobol.plugins.templates:CobTemplatesProvider'
        ],
        # workspaces
        'hackedit.plugins.workspace_providers': [
            'cobol_project_workspace = '
            'hackedit_cobol.plugins.workspaces:CobolProjectWorkspace',
            'cobol_file_workspace = '
            'hackedit_cobol.plugins.workspaces:CobolFileWorkspace'
        ]
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
