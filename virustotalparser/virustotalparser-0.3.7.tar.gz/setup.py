from setuptools import setup, find_packages
 
setup(
    name='virustotalparser',
    author='Maciej Walerczuk',
    author_email='mwalerczuk@gmail.com',
    url='http://github.com',
    license='MIT',
    version='0.3.7',
    packages=find_packages(),
    scripts=['bin/vtparser'],
    install_requires=[
          'ply==3.8'
    ],

) 
