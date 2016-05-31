from setuptools import setup

setup(
    name = 'plumb',
    packages = [
        'plumbing',
        'plumbing.aws',
        'plumbing.redis',
    ],
    version = '0.5.0',
    description = 'Connect systems via Redis, AWS SQS and SNS',

    install_requires=['boto3', 'redis'],
    tests_require=['awstestutils', 'mockredispy'],

    test_suite = 'tests.unit',

    author = 'Elvio Toccalino',
    author_email = 'elvio@spect.ro',

    keywords = ['redis', 'AWS', 'queues', 'distributed'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
        'Topic :: System :: Networking',
        'Topic :: System :: Distributed Computing',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Object Brokering',
    ]
)
