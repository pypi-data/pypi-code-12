import setuptools
import pysenseload

setuptools.setup(
    name='pysenseload',
    version=pysenseload.__version__,
    packages=setuptools.find_packages(),
    url='https://github.com/oscarsix/pySenseLoad',
    license='MIT',
    author='Oskar Malnowicz',
    author_email='oscarsix@protonmail.ch',
    description='Show system load on sense hat (RPi)',
    keywords=[
        "sense hat",
        "raspberrypi",
    ],
    install_requires=[
        'sense-hat',
        'Click',
        'daemon'
    ],
    entry_points={
        'console_scripts': [
            'pysenseload=pysenseload.pysenseload:cli',
        ],
    }
)
