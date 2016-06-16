try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

import rest_api


setup(
    name='restify',
    version=rest_api.__version__,
    description="Base wrappers for creating a REST API with Bottle",

    url="http://glow.dev.ramcloud.io/sjohnson/rest-api-template",
    author="Sean Johnson",
    author_email="sean.johnson@maio.me",

    license="Unlicense",

    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: Public Domain",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    packages=[
        'rest_api',
        'rest_api.dsn',
        'rest_api.routing',
        'rest_api.util',
    ],
    install_requires=[
        'malibu',
        'bottle',
        'raven',
    ],
    package_dir={'rest_api': 'rest_api'},
    zip_safe=True,
)
