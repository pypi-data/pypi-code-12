from setuptools import setup
setup(
    name='kallithea-auth-container-internal',
    version='1.4',

    description=(
        "Kallithea authentication plugin that accepts both container and "
        "internal authentication sources"),
    url="https://bitbucket.org/gclinch/kallithea-auth-container-internal",
    license='Apache License, Version 2.0',

    author='Graham Clinch',
    author_email='g.clinch@lancaster.ac.uk',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Version Control'],

    packages=['kallithea_auth_container_internal'],
)
