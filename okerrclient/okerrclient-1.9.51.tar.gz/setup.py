from setuptools import setup

setup(name='okerrclient',
    version='1.9.51',
    description='client for okerr cloud monitoring system',
    url='http://okerr.com/',
    author='Yaroslav Polyakov',
    author_email='xenon@sysattack.com',
    license='MIT',
    packages=['okerrclient'],
    scripts=['scripts/okerrclient'],  
    install_requires=['six', 'requests', 'psutil', 'evalidate'],
    zip_safe=False)

