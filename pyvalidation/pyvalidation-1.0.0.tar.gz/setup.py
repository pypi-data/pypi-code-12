# Always prefer setuptools over distutils
from setuptools import setup, find_packages

setup(
    name='pyvalidation',
    version='1.0.0',
    url='https://github.com/rodrigorodriguescosta/pyvalidation',
    author='Rodrigo Rodrigues',
    author_email='rodrigorodriguescosta@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    include_package_data=True,
    packages=find_packages(exclude=['test_validacao']),
    install_requires=[],
)
