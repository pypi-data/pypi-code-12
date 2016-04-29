from setuptools import setup, find_packages

import os.path

if os.path.exists('README.rst'):
    with open('README.rst') as f:
        long_description = f.read()
else:
    long_description = ""

if os.name == "nt":
    os_dependendies = ['pypiwin32>=219']
else:
    os_dependendies = []

setup(
    name = "twisted_sshtools",
    version = "2.2.1",
    url = "https://github.com/i4Ds/twisted-sshtools",
    description='Start processes via SSH with twisted.',
    long_description=long_description,
    author='Ivo Nussbaumer',
    author_email='ivo.nussbaumer@fhnw.ch',
    packages = find_packages(),
    package_data={'anypy': ['templates/*.html']},
    setup_requires=['unittest2'],
    install_requires = ['unittest2>=0.8.0',
                        'pycrypto>=2.6', 
                        'pyasn1>=0.1.7', 
                        'twisted>=15.0.0',
                        'utwist>=0.1.3', 
                        'twistit>=0.2.1',
                        'cryptography>=1.2.2'] + os_dependendies,
)
