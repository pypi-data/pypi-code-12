from setuptools import setup
from setuptools import find_packages


def read_me():
    with open('README.rst') as f:
        return f.read()

setup(
    name='measurement_stats',
    version='0.1.1',
    description=
            'Measurement statistics with uncertainties and error propagation',
    long_description=read_me(),
    url='https://github.com/sernst/Measurement_Statistics',
    author='Scott Ernst',
    author_email='swernst@gmail.com',
    license='MIT',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',

        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Physics'
    ],
    install_requires=[
        'pandas',
        'numpy',
        'six'
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
    keywords='measurements statistics error propagation',
)
