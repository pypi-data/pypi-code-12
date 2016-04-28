from distutils.core import setup

setup(
    name='PenSec',
    version='0.1.1b',
    author='konfeldt',
    author_email='tfd@konfeldt.com',
    packages=['PenSecscan'],
    scripts=['bin/PenSecscan.py', 'bin/PenSecrecon.py' , 'bin/psxgrab.py'],
    url='http://konfeldt.com',
    license='LICENSE.txt',
    description='Useful pentest-related stuff.',
    long_description=open('README.txt').read(),
)
