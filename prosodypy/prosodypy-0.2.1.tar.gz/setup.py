from setuptools import setup

setup(
    name='prosodypy',
    description='A compatibility suite to write modules in Python for Prosody'
                'XMPP Server',
    author='Sergey Dobrov',
    author_email='binary@jrudevels.org',
    version='0.2.1',
    url='https://github.com/jbinary/prosodypy',
    packages=[
        'prosodypy',
        'prosodypy.examples',
        'prosodypy.twilix_compat',
    ],
    package_data={
        'prosodypy': ['mod_prosodypy/mod_prosodypy.lua'],
    },
)
