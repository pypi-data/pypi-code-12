from setuptools import setup

setup(
    name='postageapp',
    version='0.1.1',
    description='Library for sending email via the PostageApp service',
    url='http://github.com/postageapp/postageapp-python',
    author='Scott Tadman',
    author_email='tadman@postageapp.com',
    license='MIT',
    packages=['postageapp'],
    install_requires=[
        'requests', 'ostruct'
    ],
    test_suite='py.test -s',
    tests_require=['pytest'],
    zip_safe=False
)
