from setuptools import setup, find_packages

setup(
    name='django-trackmodels-xls-ritual',
    version='0.0.1',
    namespace_packages=['grimoire', 'grimoire.django'],
    packages=find_packages(exclude=['trackmodels_xls_proj', 'trackmodels_xls_proj.*', 'sample', 'sample.*']),
    package_data={
        'grimoire.django.tracked': [
            'locale/*/LC_MESSAGES/*.*'
        ]
    },
    url='https://github.com/luismasuelli/django-trackmodels-xls-ritual',
    license='LGPL',
    author='Luis y Anita',
    author_email='luismasuelli@hotmail.com',
    description='XLSX report plugin for django-trackmodels-ritual',
    install_requires=['Django>=1.7', 'XlsxWriter>=0.8.7', 'django-trackmodels-ritual>=0.0.10']
)