from setuptools import setup, find_packages

import temp_utils


tests_require = [
    'flake8>=2.4.0',
    'pytest>=2.5.0',
]

install_requires = [
]

setup(
    name='temp-utils',
    version=temp_utils.__version__,
    author='Naphat Sanguansin',
    author_email='naphat.krit@gmail.com',
    description='A temporary file utilities',
    packages=find_packages(),
    install_requires=install_requires,
    extras_require={'tests': tests_require},
    tests_require=tests_require,
    url='https://github.com/naphatkrit/temp-utils',
    keywords=['temporary', 'temp', 'chdir',
              'temp_file', 'tempfile', 'tempdir', 'temp_dir'],
)
