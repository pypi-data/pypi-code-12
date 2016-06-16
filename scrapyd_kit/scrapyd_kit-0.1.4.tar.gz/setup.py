from os.path import join, dirname

setup_args = {
    'name': 'scrapyd_kit',
    'version': '0.1.4',
    'url': 'https://github.com/soasme/scrapyd_kit',
    'description': 'A kit for extending Scrapyd',
    'long_description': open('README.rst').read(),
    'author': 'Lin Ju',
    'maintainer': 'Lin Ju',
    'maintainer_email': 'soasme@gmail.com',
    'license': 'BSD',
    'packages': ['scrapyd_kit'],
    'include_package_data': True,
    'zip_safe': False,
    'classifiers': [
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: No Input/Output (Daemon)',
        'Topic :: Internet :: WWW/HTTP',
    ],
}

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
else:
    setup_args['install_requires'] = ['Twisted>=8.0', 'Scrapy>=0.17']

setup(**setup_args)
