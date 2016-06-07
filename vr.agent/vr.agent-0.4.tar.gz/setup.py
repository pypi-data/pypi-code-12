#!/usr/bin/python
import setuptools

params = dict(
    name='vr.agent',
    namespace_packages=['vr'],
    version='0.4',
    author='Brent Tubbs',
    author_email='brent.tubbs@gmail.com',
    url='https://bitbucket.org/yougov/vr.agent',
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        'PyYAML>=3.10',
        'redis>=2.6.2',
        'requests>=1.0.4',
        'supervisor',
        'vr.common>=2.15.2',
    ],
    entry_points={
        'console_scripts': [
            'proc_publisher = vr.agent.publisher:main',
        ],
    },
    description='Velociraptor plugins to Supervisord.',
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'backports.unittest_mock',
    ],
)
if __name__ == '__main__':
    setuptools.setup(**params)
