import setuptools

setuptools.setup(
    name="dbconfigurator",
    version="0.1.4",
    url="https://github.com/artemishealth/prometheus/tree/master/rv816/GapsInCare/Pycode/Scripts/Modules/dbconfig",

    author="Ryan Vass",
    author_email="rvsax16@gmail.com",

    description="Pip installable SQLAlchemy-style config",
    long_description=open('README.rst').read(),

    packages=setuptools.find_packages(),

    install_requires=[
           'dataset'],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
