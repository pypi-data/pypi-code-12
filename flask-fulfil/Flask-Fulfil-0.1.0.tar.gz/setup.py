'''
    Flask-Fulfil
    ------------
    Fulfil.IO for your Flask app
'''

import os

from setuptools import setup

module_path = os.path.join(os.path.dirname(__file__), 'flask_fulfil.py')
with open(module_path) as module:
     for line in module:
          if line.startswith('__version_info__'):
               version_line = line
               break

__version__ = '.'.join(eval(version_line.split('__version_info__ = ')[-1]))

setup(
    name='Flask-Fulfil',
    version=__version__,
    url='https://github.com/fulfilio/flask-fulfil',
    license='BSD',
    author='Fulfil.IO Inc.',
    author_email='hello@fulfil.io',
    description='Fulfil.IO for Flask Apps',
    long_description=__doc__,
    py_modules=['flask_fulfil'],
    zip_safe=False,
    platforms='any',
    install_requires=['Flask', 'fulfil_client'],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
