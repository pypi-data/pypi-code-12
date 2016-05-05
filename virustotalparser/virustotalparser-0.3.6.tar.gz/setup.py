from setuptools import setup, find_packages
 
setup(
    name='virustotalparser',
    author='Maciej Walerczuk',
    author_email='mwalerczuk@gmail.com',
    url='http://github.com',
    license='MIT',
    version='0.3.6',
    packages=find_packages(),
    scripts=['bin/parser'],
    install_requires=[
          'ply==3.8'
    ],

) 
