from setuptools import setup, find_packages

setup(
        name='requests_cache_mongodb',
        version='0.0.1',
        keywords=('requests', 'cache'),
        description='requests session cache with mongodb backend',
        license='MIT License',
        install_requires=['requests>=2.9'],
        author='linziyan',
        author_email='aohan237@gmail.com',
        packages=find_packages(),
        platforms='any',
)
