#!/usr/bin/python
import sys

from setuptools import setup, find_packages

needs_pytest = {'pytest', 'test'}.intersection(sys.argv)
pytest_runner = ['pytest_runner'] if needs_pytest else []

setup(
    name='vr.server',
    namespace_packages=['vr'],
    version='4.11.5',
    author='Brent Tubbs',
    author_email='brent.tubbs@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    url='https://bitbucket.org/yougov/vr.server',
    install_requires=[
        'celery-schedulers==0.0.2',
        'diff-match-patch==20121119',
        'Django>=1.8,<1.9',
        'django-celery>=3.1.17,<3.2',
        'django-extensions==1.5.9',
        'django-picklefield==0.2.0',
        'django-redis-cache==0.9.5',
        'django-reversion==1.9.3',
        'django-tastypie==0.12.2',
        'Fabric3bis',
        'flower>=0.9.0,<1',
        'gevent>=1.1rc1,<2',
        'psycogreen',
        'gunicorn==0.17.2',
        'psycopg2>=2.4.4,<2.5',
        'pymongo>=2.5.2,<4',
        'redis>=2.6.2,<3',
        'requests',
        'setproctitle',
        'sseclient==0.0.8',
        'six>=1.4',
        'vr.events>=1.2.1',
        'vr.common>=4.4',
        'vr.builder>=1.3',
        'vr.imager>=1.2',
        'django-yamlfield',
        'backports.functools_lru_cache',
    ],
    entry_points = {
        'console_scripts': [
            'vr_worker = vr.server.commands:start_celery',
            'vr_beat = vr.server.commands:start_celerybeat',
            'vr_migrate = vr.server.commands:run_migrations',
        ],
    },
    description=("Velociraptor's Django and Celery components."),
    setup_requires=[
    ] + pytest_runner,
    tests_require=[
        'pytest',
        'backports.unittest_mock',
        'jaraco.mongodb>=3.11',
        'python-dateutil>=2.4',
        'jaraco.postgres>=1.3.1',
    ],
)
