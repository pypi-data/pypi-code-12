from setuptools import setup
import os

setup(
    name='segment_source',
    packages=['segment_source'],
    version='0.0.4',
    description='Python source client',
    author='Segment',
    author_email='friends@segment.com',
    url='https://github.com/segmentio/python-source',
    install_requires=[
        'jsonrpc-requests==0.2',
        'simplejson==3.8.2',
        'websocket-client==0.37.0'
    ]
)
