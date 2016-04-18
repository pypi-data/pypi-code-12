from setuptools import setup

setup(
    name='uncompyle2',
    version='2.0.0',
    description='Python byte-code to source-code converter',
    long_description=open("README.rst").read(),
    author='Hartmut Goebel',
    author_email='h.goebel@crazy-compilers.com',
    license="MIT",
    url='https://github.com/rocky/python-uncompyle6',
    packages=[],
    install_requires=['uncompyle6'],
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
)
