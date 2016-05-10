import os
from setuptools import setup, find_packages

import templatingbwc
version = templatingbwc.VERSION

cdir = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(cdir, 'readme.rst')).read()
CHANGELOG = open(os.path.join(cdir, 'changelog.rst')).read()

setup(
    name = "TemplatingBWC",
    version = version,
    description = "A BlazeWeb component with template themes",
    long_description=README + '\n\n' + CHANGELOG,
    author = "Randy Syring",
    author_email = "rsyring@gmail.com",
    url='http://bitbucket.org/rsyring/templatingbwc/',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP'
      ],
    license='BSD',
    packages=find_packages(exclude=['templatingbwc_*']),
    include_package_data = True,
    install_requires = [
        'BlazeForm>=0.3.0',
        'BlazeWeb>0.4.4',
    ],
    zip_safe=False
)
