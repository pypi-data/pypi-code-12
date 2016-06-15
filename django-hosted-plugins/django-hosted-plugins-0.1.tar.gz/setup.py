import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-hosted-plugins',
    version='0.1',
    description='Self host third-party plugins that work alongside your project.',
    long_description=README,
    url='https://pypi.python.org/pypi/django-hosted-plugins/',
    author='Vimal Aravindashan',
    author_email='vimal.aravindashan@gmail.com',
    license='MIT License',
    install_requires=[
        'django>=1.8,<2',
        'djangorestframework>=3.0,<3.4',
    ],
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
