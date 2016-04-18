from setuptools import setup, find_packages

module_name = 'docido-python-sdk'
root_url = 'https://github.com/cogniteev/' + module_name

__version__ = None
with open('docido_sdk/__init__.py') as istr:
    for l in filter(lambda l: l.startswith('__version__ ='), istr):
        exec(l)

setup(
    name='docido-sdk',
    version=__version__,
    description='Docido software development kit for Python',
    author='Cogniteev',
    author_email='tech@cogniteev.com',
    url=root_url,
    download_url=root_url + '/tarball/' + __version__,
    license='Apache license version 2.0',
    keywords='cogniteev docido',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Libraries',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Operating System :: OS Independent',
        'Natural Language :: English',
    ],
    packages=find_packages(exclude=['*.tests']),
    test_suite='docido.sdk.test.suite',
    zip_safe=True,
    install_requires=[
        'elasticsearch==2.3.0',
        'ProxyTypes==0.9',
        'python-dateutil>=2.5.2',
        'pytz>=2015.6',
        'requests>=2.8.1',
        'setuptools>=0.6',
        'six>=1.10.0',
        'yamlious>=0.2.1',
    ],
    entry_points="""
        [console_scripts]
        dcc-run = docido_sdk.scripts.dcc_run:run
    """
)
