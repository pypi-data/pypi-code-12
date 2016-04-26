from setuptools import setup, find_packages

setup(
    name='pyaudioduplexfinder',
    version='0.2.8',
    packages=find_packages(),
    include_package_data=True,
    url='https://pyaudioduplexfinder.b1t.uk',
    license='MIT',
    author='Oskar Malnowicz',
    author_email='8@b1t.uk',
    description='Find duplicate in audio files',
    py_modules=['pyauduxfind'],
    install_requires=[
        'Click',
        'colorama',
        'pyyaml'
    ],
    entry_points={
        'console_scripts': [
            'pyaudioduplexfinder=pyaudioduplexfinder.pyauduxfind:cli',
        ],
    }
)
