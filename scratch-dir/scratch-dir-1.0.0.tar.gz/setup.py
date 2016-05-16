# https://coderwall.com/p/qawuyq
# Thanks James.

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    long_description = ''
    print 'warning: pandoc or pypandoc does not seem to be installed; using empty long_description'

from setuptools import setup

setup(
    name='scratch-dir',
    version=__import__('scratch_dir').__version__,
    author='Body Labs',
    author_email='paul.melnikow@bodylabs.com, alex@bodylabs.com, david.smith@bodylabs.com',
    description='Unit test mixin which creates a scratch directory',
    long_description=long_description,
    url='https://github.com/bodylabs/scratch-dir',
    license='MIT',
    py_modules=[
        'scratch_dir',
    ],
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)
