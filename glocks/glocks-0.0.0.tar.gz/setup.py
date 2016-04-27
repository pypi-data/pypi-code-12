from setuptools import setup, find_packages
import glocks


setup(
    author="Anthony Almarza",
    name="glocks",
    version=glocks.__version__,
    packages=find_packages(exclude=["test*", ]),
    url="https://github.com/anthonyalmarza/glocks",
    description=(
        "``glocks`` is a set of global locks that use redis to "
        "register the locked resource. Variants of the simple (non-reentrant) "
        "global lock include reentrant, distrubed and reentrant-distributed "
        "locks."
    ),
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    keywords=[
        'glocks', 'global locks', 'lock', 'global', 'locks', 'reentrant',
        'distributed', 'redis', 'twisted'
    ],
    install_requires=[
        'redis', 'hiredis', 'twisted'
    ],
    extras_require={'dev': ['ipdb', 'mock', 'tox']},
    include_package_data=True
)
