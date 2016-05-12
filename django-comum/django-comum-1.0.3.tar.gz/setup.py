# coding: utf-8
from setuptools import setup, find_packages
 
setup(
    name='django-comum',
    version='1.0.3',
    description='Pluggable django app for commom models and utilities.',
    long_description='Pluggable django app for commom models and utilities.',
    author='SIGMA Geosistemas',
    author_email='atendimento@consultoriasigma.com.br',
    maintainer='SIGMA Geosistemas',
    maintainer_email='atendimento@consultoriasigma.com.br',
    url='https://gitlab.sigmageosistemas.com.br/dev/django-usuarios/',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Pillow',
        'django',
        'django-municipios'
    ],
    classifiers=[
        'Framework :: Django',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
        'Natural Language :: Portuguese (Brazilian)'
    ],
)
