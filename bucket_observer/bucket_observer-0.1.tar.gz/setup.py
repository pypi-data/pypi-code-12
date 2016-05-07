from setuptools import setup


setup(
    name='bucket_observer',
    packages=['bucket_observer'],
    version='0.1',
    description='Pulls S3 buckets, observes changes and emits blinker signals.',
    author='Fabian Topfstedt',
    author_email='topfstedt@schneevonmorgen.com',
    url='https://bitbucket.org/fabian/bucket_observer',
    keywords=['s3', 'bucket', 'observer'],
    classifiers=[],
    install_requires=[
        'blinker',
        'boto3',
        'tinydb',
    ]
)
