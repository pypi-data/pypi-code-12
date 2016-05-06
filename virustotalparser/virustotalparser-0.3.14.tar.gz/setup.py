from setuptools import setup, find_packages
 
setup(
    name='virustotalparser',
    author='Maciej Walerczuk',
    author_email='mwalerczuk@gmail.com',
    url='https://github.com/mwalercz/vtparser',
    license='MIT',
    version='0.3.14',
    packages=find_packages(),
    scripts=['bin/vtparser'],
    install_requires=[
          'ply==3.8'
    ],

) 
