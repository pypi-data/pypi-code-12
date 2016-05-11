from setuptools import setup

setup(
    name='mym2m-client',
    version='0.1.0',
    packages=['mym2m'],
    install_requires=[
      'requests',
    ],
    license='MIT',
    author='360 Telemetry',
    author_email='info@360telemetry.com',
    long_description=open('README.md').read(),
    description='Python SDK for the MyM2M Web JSON Device API',
    url='https://bitbucket.org/360telemetry/mym2m-python-sdk'
)
