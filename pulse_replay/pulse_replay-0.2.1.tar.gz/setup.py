from setuptools import setup, find_packages


required = [
    "MozillaPulse",
    "mock",
]

setup(
    author='Armen Zambrano G.',
    author_email='armenzg@mozilla.com',
    name='pulse_replay',
    install_requires=required,
    license='MPL',
    packages=find_packages(),
    url='https://github.com/armenzg/pulse_replay',
    version='0.2.1',
)
