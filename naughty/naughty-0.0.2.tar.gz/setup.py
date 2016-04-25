from setuptools import find_packages, setup


version = '0.0.2'


setup(
    author='WildFoundry Ltd',
    author_email='info@wildfoundry.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    description='A collection of lists of naughty words for use in software development',
    install_requires=(),
    license='LGPL',
    name='naughty',
    packages=find_packages(exclude=['tests']),
    url='https://github.com/wildfoundry/naughtywords/',
    version=version,
)
