from setuptools import find_packages, setup

setup(
    name='ddnspod',
    version='0.2.0',
    url='https://github.com/maguowei/ddnspod',
    license='The MIT License (MIT)',
    author='maguowei',
    author_email='imaguowei@gmail.com',
    description='ddnspod',
    packages=find_packages(),
    install_requires=[
        'requests>=2.9.1',
    ],
    classifiers=(
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ),
)
