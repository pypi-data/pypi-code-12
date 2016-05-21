try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='python-boatdclient',
    version='0.4.1',
    author='Louis Taylor',
    author_email='louis@kragniz.eu',
    description=('Python wrapper for the boatd API, used to write behavior scripts.'),
    long_description=open("README.rst").read(),
    license='GPL',
    keywords='boat sailing wrapper rest',
    url='https://github.com/boatd/python-boatd',
    packages=['boatdclient'],
    scripts=['boatdctl'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ],
)
