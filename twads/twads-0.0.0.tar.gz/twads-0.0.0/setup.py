import re
from distutils.core import setup


with open('VERSION', 'r') as f:
    try:
        version = re.search('^([0-9.]*)', f.read()).group(1)
    except AttributeError:
        raise RuntimeError('Version not found')


setup(
    name='twads',
    packages=['twads'],
    version=version,
    description='A wrapper for the Twitter Ads API',
    author='Jacob Gillespie',
    author_email='jdgillespie91@gmail.com',
    url='https://github.com/jdgillespie91/twads'
)
