from pathlib import Path

from setuptools import setup, find_packages

from golgi.config.write import write_pkg_config

write_pkg_config('.', Path('tek_utils.conf'), 'tek_utils')
write_pkg_config('.', Path('sharehoster.conf'), 'sharehoster')

version_parts = (3, 1, 2)
version = '.'.join(map(str, version_parts))

setup(
    name='tek_utils',
    version=version,
    packages=find_packages(exclude=['tests', 'tests.*']),
    data_files=[('share/tek_utils/config',
                 ['tek_utils.conf', 'sharehoster.conf'])],
    install_requires=[
        'requests',
        'tek>=3.0.0',
        'lxml',
        'ThePirateBay',
        'pyquery',
    ],
    entry_points={
        'console_scripts': [
            'iptabler = tek_utils.iptables:iptabler',
            'extract = tek_utils.extract:extract',
            'shget = tek_utils.sharehoster:shget',
            'tget = tek_utils.sharehoster:tget',
            'sh_release = tek_utils.sharehoster.search:sh_release',
            'gain_collection = tek_utils.gain:gain_collection',
            'process_album = tek_utils.process_album:process_album',
        ]
    }
)
