from setuptools import setup, find_packages


setup(
    name='aiomas',
    version='1.0.3',
    author='Stefan Scherfke',
    author_email='stefan.scherfke at offis.de',
    description=('Asyncio-based, layered networking library providing '
                 'request-reply channels, RPC, and multi-agent systems.'),
    long_description=(open('README.rst', encoding='utf-8').read() + '\n\n' +
                      open('CHANGES.rst', encoding='utf-8').read() + '\n\n' +
                      open('AUTHORS.rst', encoding='utf-8').read()),
    url='https://aiomas.readthedocs.io',
    install_requires=[
        'arrow>=0.7',
    ],
    extras_require={
        'mp': ['msgpack-python>=0.4.7'],
        'mpb': ['blosc>=1.3.2', 'msgpack-python>=0.4.7'],
    },
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    entry_points={
        'console_scripts': [
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
