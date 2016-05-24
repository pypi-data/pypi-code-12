from distutils.core import setup
from setuptools import find_packages
from parrot import __version__


setup(
    name='parrot',
    version=__version__,
    description='Python lib for parsing sites',
    license='BSD',
    author='Stanislav Karpov',
    author_email='iam@stkrp.ru',
    url='https://bitbucket.org/stkrp/parrot/',
    packages=find_packages(),
    install_requires=[
        # 'lxml==3.4.4',       # required for selector.selectors.XpathSelector
        # 'peewee==2.6.4',     # required for storage.storages.PeeweeStorage
        # 'selenium==2.48.0',  # required for loader.loaders.SeleniumLoader
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
