import sys
from setuptools import setup

dependencies = ['psycopg2==2.6.1']
if sys.version_info < (3, 4):
    dependencies.append('pathlib==1.0.1')


setup(
    name='amigrations',
    version='0.5',
    description=('Ascetic database migrations. The most ease way to power your'
                 ' python app with raw database migrations'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Intended Audience :: Developers',
        'Topic :: Database',
    ],
    url='https://github.com/sergeyglazyrindev/amigrations',
    author='Sergey Glazyrin',
    author_email='sergey.glazyrin.dev@gmail.com',
    license='MIT',
    packages=['amigrations', 'amigrations.adapters'],
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'testing': ['nose', 'mock'],
    },
    test_suite='tests',
    keywords=['database', 'migration'],
    download_url=('https://github.com/sergeyglazyrindev/'
                  'amigrations/tarball/0.5'),
    install_requires=dependencies
)
