# -*- coding: utf-8 -*-
"""
Setup for the :mod:`django_turnit` application
"""
from setuptools import setup, find_packages

# Main setup function
setup(name='django_turnit',
      version='0.2.1a1',
      description='PDF thumbnailer and viewer for django applications',
      packages=find_packages(),
      install_requires=[
          # docutils inclusion for .rst files
          'docutils>=0.3',
          # django inclusion, tested with 1.8/1.9 only
          'django>=1.8, <1.10',
          # Application config
          'django-appconf>=1.0',
          # PDF exploration
          'pdfminer',
          # Thumbnailing
          'easy-thumbnails'
      ],
      author='François GUÉRIN',
      author_email='frague59@gmail.com',
      license='Modified BSD',
      url='https://gitlab.com/frague59/django-turnit',
      download_url='https://gitlab.com/frague59/django-turnit/repository/archive.zip?ref=master',
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'Framework :: Django :: 1.8',
                   'Framework :: Django :: 1.9',
                   'Programming Language :: Python :: 2.7',
                   'License :: OSI Approved :: BSD License', ],
      keywords=['django', 'PDF', 'turn.js'],
      )
