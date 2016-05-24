# Always prefer setuptools over distutils
from setuptools import setup, find_packages

setup(
    name='pyservice_django',
    version='1.1.64',
    url='https://github.com/rodrigorodriguescosta/pyservice_django',
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
    packages=find_packages(),
    install_requires=['django>=1.8'],
)
