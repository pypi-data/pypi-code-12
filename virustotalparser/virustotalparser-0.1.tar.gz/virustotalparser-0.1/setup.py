from setuptools import setup
 
setup(
    name='virustotalparser',    # This is the name of your PyPI-package.
    version='0.1',                          # Update the version number for new releases
    scripts=['bin/parser'],                  # The name of your scipt, and also 
    install_requires=[
          'ply',
    ],
    author='Maciej Walerczuk'
    
) 
