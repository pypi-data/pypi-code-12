from setuptools import find_packages, setup


LONG_DESCRIPTION = """\
CloudSight API for Python
=========================

A simple CloudSight API Client for Python programming language. It has been
tested with Python versions 2.7 and 3.5."""


setup(
    name='cloudsight',
    version='0.9.2',
    description='CloudSight API library for Python',
    long_description=LONG_DESCRIPTION,
    license='MIT',
    author='CloudSight',
    author_email='miGlanz@gmail.com',
    url='https://github.com/cloudsight/cloudsight-python',
    packages=find_packages(),
    install_requires=['requests'],
    keywords='cloudsight library',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    zip_safe=True,
)
