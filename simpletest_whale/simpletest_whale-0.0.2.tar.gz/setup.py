from setuptools import setup, find_packages
import simpletest_whale

setup(
        name = 'simpletest_whale',
        version = simpletest_whale.__version__,
        keywords =('whale'),
        description = 'a simple test',
        license = 'MIT License',
        install_requires = ['simplejson>=1.1'],

        author ='WhaleChen',
        author_email = 'whalechen123@gmail.com',

        packages = find_packages(),
        entry_points={
            'console_scripts': [
                'simpletest_whale = simpletest_whale.lines_pretty:hello',
                ]
            },
        platforms = 'any',
        )

