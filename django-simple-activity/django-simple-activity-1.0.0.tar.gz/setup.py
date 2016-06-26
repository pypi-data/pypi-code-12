import os
from setuptools import setup, find_packages

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()

setup(
    name='django-simple-activity',
    version='1.0.0',
    packages=find_packages('src', exclude=('tests',)),
    package_dir={'': 'src'},
    include_package_data=True,
    license='Apache 2.0',
    description=(
        'Simple, generic, activity streams '
        'from the actions on your site.'),
    url='https://github.com/richardasaurus/django-simple-activity',
    author='Richard O\'Dwyer',
    author_email='richard@richard.do',
    zip_safe=True,
    install_requires=install_requires
)
