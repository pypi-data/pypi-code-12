from setuptools import setup, find_packages
 
setup(
    name='virustotalparser',    
    version='0.3.1',
    packages=find_packages(),
    scripts='bin/parser',                  
    install_requires=[
          'ply',
    ],
    author='Maciej Walerczuk'
    
) 
