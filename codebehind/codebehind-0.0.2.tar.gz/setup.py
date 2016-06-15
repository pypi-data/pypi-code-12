import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()


setup(
    name='codebehind',
    version='0.0.2',
    packages=['codebehind'],
    description='A collection of magic',
    long_description=README,
    author='Michael Henry Pantaleon',
    author_email='me@iamkel.net',
    url='https://github.com/michaelhenry/codebehind/',
    license='MIT',
    install_requires=[
        'Django>=1.9','djangorestframework==3.3.3',
    ]
)
