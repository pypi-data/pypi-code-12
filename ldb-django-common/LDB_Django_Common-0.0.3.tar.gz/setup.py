from setuptools import setup

setup(name='LDB_Django_Common',
      version='0.0.3',
      description="""
Common utility functions and classes for django.""",
      author='Alex Orange',
      author_email='alex@eldebe.org',
      packages=['ldb', 'ldb.django', 'ldb.django.test', 'ldb.django.contrib',
                'ldb.django.contrib.auth'],
      namespace_packages=['ldb', 'ldb.django'],
      url='http://www.eldebe.org/ldb/django/common/',
      license='BSD',
      setup_requires=['setuptools_hg'],
      install_requires=['Django>=1.9.1'],
     )
