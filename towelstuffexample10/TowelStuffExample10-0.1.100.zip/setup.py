from distutils.core import setup

setup(
    name='TowelStuffExample10',
    version='0.1.100',
    author='xyz',
    author_email='navforpython@gmail.com',
    packages=['towel_stuff', 'towel_stuff.test'],
    scripts=['bin/stowe-towels.py', 'bin/wash-towels.py'],
    url='http://pypi.python.org/pypi/TowelStuff/',
    license='LICENSE.txt',
    description='Useful towel-related stuff.',
    long_description=open('README.txt').read(),
)
