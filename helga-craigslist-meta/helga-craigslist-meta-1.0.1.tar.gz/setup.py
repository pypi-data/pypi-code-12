from parse_requirements_not_suckily import parse_requirements
from setuptools import setup, find_packages
from helga_craigslist_meta import __version__ as version

setup(
    name='helga-craigslist-meta',
    version=version,
    description=('Provide information for craigslist related metadata'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Communications :: Chat :: Internet Relay Chat',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Chat :: Internet Relay Chat'],
    keywords='irc bot craigslist-meta',
    author='Jon Robison',
    author_email='narfman0@gmail.com',
    url='https://craigslist.com/narfman0/helga-craigslist-meta',
    license='LICENSE',
    packages=find_packages(),
    include_package_data=True,
    py_modules=['helga_craigslist_meta.plugin'],
    zip_safe=True,
    install_requires=parse_requirements(),
    test_suite='',
    entry_points=dict(
        helga_plugins=[
            'craigslist-meta = helga_craigslist_meta.plugin:craigslist_meta',
        ],
    ),
)
