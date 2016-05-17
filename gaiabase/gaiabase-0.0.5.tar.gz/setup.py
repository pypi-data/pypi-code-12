from distutils.core import setup

setup(
    name='gaiabase',
    version='0.0.5',
    author='Mingli Yuan',
    author_email='mingli.yuan@gmail.com',
    packages=['gaia','gaia.cloud','gaia.db'],
    package_dir={'gaia': 'gaia'},
    url='https://github.com/caiyunapp/gaiabase.git',
    license='LICENSE',
    description='The base library for gaia-based projects',
    install_requires=[
        "PyYAML"
    ],
)
