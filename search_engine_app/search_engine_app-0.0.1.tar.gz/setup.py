from setuptools import setup, find_packages
from os.path import join, dirname
import search_engine_app


setup(
    name='search_engine_app',
    version = "0.0.1",
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.txt')).read(),
    install_requires=[
        'Flask',
        'validators',
        'urllib3',
        'urlparse3',
        'cookiejar',
        'bs4'
    ],
    entry_points={
       'console_scripts': [
           'serve = search_engine_app.serve',
           ]
   }
)
