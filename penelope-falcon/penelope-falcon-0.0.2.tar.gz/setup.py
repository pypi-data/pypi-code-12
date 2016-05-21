from setuptools import setup


setup(
    name='penelope-falcon',
    version='0.0.2',
    author='Brian Hines',
    author_email='brian@projectweekend.net',
    description='My collection of assorted utils for the Falcon Framework (http://falconframework.org/)',
    url='https://github.com/projectweekend/penelope',
    packages=['penelope'],
    py_modules=['penelope'],
    install_requires=[
        'bcrypt>=2.0.0',
        'falcon>=1.0.0',
        'itsdangerous>=0.24'
    ],
)
