import re
import sys
import os
from setuptools import setup, find_packages

PY_VER = sys.version_info

if PY_VER < (3, 4):
    raise RuntimeError("aio_periodic_task doesn't support Python version prior 3.3")

def read(*parts):
    with open(os.path.join(*parts), 'rt') as f:
        return f.read().strip()

def read_version():
    regexp = re.compile(r"^__version__\W*=\W*'([\d.abrc]+)'")
    init_py = os.path.join(os.path.dirname(__file__),
                           'aio_periodic_task', '__init__.py')
    with open(init_py) as f:
        for line in f:
            match = regexp.match(line)
            if match is not None:
                return match.group(1)
        raise RuntimeError('Cannot find version in aio_periodic_task/__init__.py')

classifiers = [
    'License :: OSI Approved :: MIT License',
    'Development Status :: 3 - Alpha',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Operating System :: POSIX',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries',
]

setup(name='aio_periodic_task',
      version=read_version(),
      description='periodic task for asyncio',
      long_description="\n\n".join((read('README.md'))),
      classifiers=classifiers,
      platforms=["POSIX"],
      author="Sick Yoon",
      author_email="shicky@gmail.com",
      url="https://github.com/shicky/aio_periodic_task",
      download_url="https://github.com/shicky/aio_periodic_task/tarball/0.1.0",
      keywords=['asyncio', 'aio-libs', 'aiohttp'],
      license="MIT",
      packages=find_packages(exclude=["tests"]),
      install_requires=[],
      include_package_data=True)

