from setuptools import setup
setup(
    name='cherrypy-psycopg2',
    version='1.1',

    description="CherryPy tool to manage Psycopg 2 database connections",
    url="https://bitbucket.org/gclinch/cherrypy-psycopg2",
    license='Apache License, Version 2.0',

    author='Graham Clinch',
    author_email='g.clinch@lancaster.ac.uk',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: CherryPy',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Database'],

    packages=['cherrypy_psycopg2'],
    install_requires=['CherryPy', 'psycopg2'],
)
