import os

from setuptools import setup, find_packages

this = os.path.dirname(os.path.realpath(__file__))


def read(name):
    with open(os.path.join(this, name)) as f:
        return f.read()


setup(
    name='ps_crud',
    version='0.0.4',
    url='http://github.com/sacrud/ps_crud/',
    author='Svintsov Dmitry',
    author_email='sacrud@uralbash.ru',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    license="MIT",
    description='CRUD templates for pyramid_sacrud Web interface.',
    long_description=read('README.rst'),
    install_requires=read('requirements.txt'),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Framework :: Pyramid ",
        "Topic :: Internet",
        "Topic :: Database",
    ],
)
