from setuptools import setup
from os.path import join, dirname

requirements = [
    'urllib3==1.7.1'
]

version = open(join(dirname(__file__), 'version')).read().strip()
print(version)


setup(
    name='coin',
    version=version,
    py_modules=['coinlib.debian', 'coinlib.python', 'coinlib.raw', 'coinlib.util'],
    install_requires=requirements,
    scripts=['coin'],
    description='Copy Installer',
    license='GPLv3',
    author='Syncloud',
    author_email='support@syncloud.it',
    url='https://github.com/syncloud/coin'
)
