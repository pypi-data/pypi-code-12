import setuptools

setuptools.setup(
    name='pySenseLoad',
    version='0.1.0',
    packages=setuptools.find_packages(),
    url='https://github.com/oscarsix/pySenseLoad',
    license='MIT',
    author='Oskar Malnowicz',
    author_email='oscarsix@protonmail.ch',
    description='Show system load on sense hat (RPi)',
    install_requires=['numpy', 'Click'],
    entry_points={
        'console_scripts': [
            'pysenseload=pysenseload.pysenseload:cli',
        ],
    }
)
