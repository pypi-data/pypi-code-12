from setuptools import setup, find_packages

setup(
    name='chswt',
    version='0.0.2',
    author='Konstantin Kruglov',
    author_email='kruglovk@gmail.com',
    description='Channel switcher',
    # long_description='',
    url='https://github.com/k0st1an/chswt',
    packages=find_packages(),
    install_requires=[],
    scripts=['chswt.py'],
    keywords=('network', 'route', 'switcher'),
    license='Apache License Version 2.0',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only',
    ],
)
