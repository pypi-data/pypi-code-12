
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='exportable',
    version='0.1.2',
    packages=[
        'exportable',
        'exportable.exporters',
        'exportable.exporters.tests'
    ],
    package_data={
        '*': ['LICENSE.txt', 'requirements.txt'],
    },
    url='https://github.com/amcat/exportable',
    license='AGPL',
    author='AmCAT Developers',
    author_email='',
    description='',
    install_requires=[
        "python-dateutil",
        "pyexcel",
        "pyexcel-io",
        "pyexcel-ods3",
        "pyexcel-xlsx",
        "pyexcel-xls",
        "typing"
    ]
)
