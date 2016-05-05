from setuptools import setup, find_packages
 
setup(
    name='virustotalparser',    
    version='0.3.4',
    packages=find_packages(),
    scripts='bin/parser.py',
    install_requires=[
          'ply'
    ],

) 
