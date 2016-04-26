from setuptools import setup, find_packages

setup(
    name='pyaudioduplexfinder',
    version='0.3.1',
    packages=find_packages(),
    include_package_data=True,
    url='https://pyaudioduplexfinder.b1t.uk',
    license='MIT',
    author='Oskar Malnowicz',
    author_email='8@b1t.uk',
    description='Find duplicate in audio files',
    install_requires=[
        'Click',
        'colorama',
        'pyyaml',
        'pyprind'
    ],
    entry_points={
        'console_scripts': [
            'pyaudioduplexfinder=pyaudioduplexfinder.pyauduxfind:cli',
        ],
    }
)
