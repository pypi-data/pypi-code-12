import minitest
from distutils.core import setup


cur_classifiers = [
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 3",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Topic :: Software Development :: Libraries",
    "Topic :: Utilities",
]

setup(
    name='minitest',
    version=minitest.__version__,
    author='Colin Ji',
    author_email='jichen3000@gmail.com',
    packages=['minitest'],
    url='https://pypi.python.org/pypi/minitest',
    description='Minitest is inspired by Ruby minispec.',
    long_description=open('README.txt').read(),
    license="MIT",
    classifiers=cur_classifiers    
)
