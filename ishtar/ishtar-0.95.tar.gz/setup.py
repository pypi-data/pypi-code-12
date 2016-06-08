# -*- coding: utf-8 -*-
import os
from setuptools import setup  # , find_packages
import version

try:
    reqs = open(os.path.join(os.path.dirname(__file__),
                             'requirements.txt')).read()
except (IOError, OSError):
    reqs = ''

setup(
    name='ishtar',
    version=version.get_version(),
    description="Ishtar is a database to manage the finds and "
                "documentation from archaeological operations.",
    long_description=open('README.rst').read(),
    author=u'Étienne Loks',
    author_email='etienne.loks@iggdrasil.net',
    url='http://ishtar-archeo.net/',
    license='AGPL v3 licence, see COPYING',
    packages=[
        'archaeological_finds', 'example_project',
        'archaeological_warehouse', 'archaeological_files_pdl',
        'archaeological_files', 'xhtml2odt', 'simple_history', 'ishtar_common',
        'archaeological_operations', 'archaeological_context_records',
        'ishtar_pdl'],
    include_package_data=True,
    install_requires=reqs,
    # test_suite = "",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
    ]
)
