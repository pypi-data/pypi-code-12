from setuptools import setup, find_packages

setup(
    name='pyaudioduplexfinder',
    version='0.1.1',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    url='https://pyaudioduplexfinder.b1t.uk',
    license='MIT',
    author='Oskar Malnowicz',
    author_email='8@b1t.uk',
    description='Find duplicate in audio files',
    entry_points={
        'console_scripts': [
            'pyaudioduplexfinder=pyaudioduplexfinder:main',
        ],
    }
)
