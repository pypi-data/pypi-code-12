import os
from setuptools import setup, find_packages

import allauth_bootstrap


# See https://pypi.python.org/pypi?%3Aaction=list_classifiers
CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Internet :: WWW/HTTP :: WSGI',
    'Topic :: Software Development :: Libraries :: Python Modules',
]


setup(
    name='django-allauth-bootstrap',
    version=allauth_bootstrap.__version__,
    url='https://bitbucket.org/cschur/django-allauth-bootstrap',
    author='Chris Schur',
    author_email='chris.schur@gmx.de',
    description='Twitter Bootstrap Layout for Django Allauth',
    long_description=open(
        os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    license='BSD License',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    install_requires=[
        'Django >=1.9, <1.10',
        'django-allauth >=0.19, <0.26',
        'django-bootstrap-form >=3.2, <4.0',
    ],
    tests_require=[
    ],
    packages=find_packages(exclude=["docs", "exampleproject", "tests"]),
    # TODO: When ``package_data`` collects files as expected, us that one
    # instead of ``MANIFEST.in`` and ``include_package_data``.
    # package_data={'': ['*.html', '*.txt', '*.mo']},
    include_package_data=True,
    zip_safe=False,
    keywords=["django", "allauth", "Twitter", "Bootstrap", "website"]
)
