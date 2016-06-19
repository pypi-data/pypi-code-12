from distutils.core import setup

from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()



setup(
    name='hms_base',
    version='1.0.1',
    packages=['hms_base', 'hms_base.tests'],

    url='https://github.com/haum/hms_base',
    license='MIT',

    author='Romain Porte (microjoe)',
    author_email='microjoe@microjoe.org',

    description='Base package for HAUM micro-services',
    long_description=long_description,

    classifiers = [
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',

        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    install_requires=['pika']
)
