from setuptools import setup, find_packages


VERSION = '0.1-alpha.7'

setup(
    name='plugandpie',
    version=VERSION,
    description='Device driver and automation for common sensors',
    author='Victor Villas',
    author_email='villasv@outlook.com',
    license='GPLv3+',
    url='https://github.com/villasv/plugandpie',
    packages=find_packages(),
    include_package_data=True,
    long_description=open('README.rst').read(),
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 2.7",
        "Development Status :: 3 - Alpha ",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    keywords='plugandpie plug and play raspberry pi sensors',
    install_requires=[
    ],
    extras_require={
        ':python_version < "3.4"': [
            'enum34'
        ]
    }
)
