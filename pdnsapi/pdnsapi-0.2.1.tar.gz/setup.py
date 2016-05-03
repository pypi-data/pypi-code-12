from setuptools import setup

setup(
    name='pdnsapi',
    version='0.2.1',
    description='Library for connecting to PowerDNS 3.4 REST API',
    author='Erik Lundberg',
    author_email='lundbergerik@gmail.com',
    packages=['pdnsapi'],
    include_package_data=True,
    install_requires=['requests'],
    zip_safe=False,
    classifiers=(),
    tests_require=['mock'],
    test_suite='tests.test_pdnsapi'
)
