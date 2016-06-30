from setuptools import setup
setup(
    name='pgtask-worker',
    version='1.10',

    description="Worker library for Postgres pgtask event queue",
    url="https://bitbucket.org/gclinch/pgtask",
    license='Apache License, Version 2.0',

    author='Graham Clinch',
    author_email='g.clinch@lancaster.ac.uk',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: System :: Distributed Computing'],

    packages=['pgtask_worker'],
    install_requires=['psycopg2'],
)
