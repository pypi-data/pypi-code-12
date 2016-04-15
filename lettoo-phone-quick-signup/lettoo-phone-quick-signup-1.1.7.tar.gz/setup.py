# -*- coding: utf-8 -*-
"""Setup file for easy installation"""
from os.path import join, dirname
from setuptools import setup


version = __import__('phone_quick_signup').__version__

LONG_DESCRIPTION = """
Lettoo Phone Quick Signup is an easy to setup authentication/registration
mechanism for Django projects.
"""


def long_description():
    """Return long description from README.rst if it's present
    because it doesn't get installed."""
    try:
        return open(join(dirname(__file__), 'README.rst')).read()
    except IOError:
        return LONG_DESCRIPTION


setup(name='lettoo-phone-quick-signup',
      version=version,
      author='Mingyu Gu',
      author_email='mingyugu0410@gmail.com',
      description='Django social authentication made simple.',
      license='BSD',
      keywords='django, openid, oauth, social auth, application',
      url='https://mingyugu@bitbucket.org/lettoo/lettoo_phone_quick_signup.git',
      packages=['phone_quick_signup',
                'phone_quick_signup.migrations',
                'phone_quick_signup.backends'],
      long_description=long_description(),
      install_requires=['django>=1.9.2',
                        'djangorestframework>=3.3.2'],
      classifiers=['Framework :: Django',
                   'Development Status :: 4 - Beta',
                   'Topic :: Internet',
                   'License :: OSI Approved :: BSD License',
                   'Intended Audience :: Developers',
                   'Environment :: Web Environment',
                   'Programming Language :: Python :: 2.5',
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7'],
      zip_safe=False)
