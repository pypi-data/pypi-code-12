from setuptools import setup
import os,sys

# Following Lapin example
# https://bitbucket.org/CVisionLab/cvl-python/src/51308c1155a6242fbb914870732187adfc8881f0/setup.py?at=default&fileviewer=file-view-default

root_pkg = 'cvlops'

# find all subpackages
root = os.path.join(os.path.dirname(__file__), root_pkg)

packages = []
for subdir, _, _ in os.walk(root):
        subpath = subdir[len(root):].replace(os.path.sep, '.')
        packages.append(root_pkg + subpath)

setup(
    name=root_pkg,
    description='CVISIONLAB OPS Python Utils',
    long_description=open('README.txt').read(),
    version='1.14',
    author='Skubriev Vladimir',
    author_email='skubriev@cvisionlab.com',
    license='GPL',
    url='https://github.com/cvisionlabops/cvlops-python',
    install_requires=[
                  'jinja2'
    ],
    packages=packages,
    package_data={'cvlops': ['jinja2/*.jinja2']},
    #data_files=[('jinja2',['jinja2'])],
    include_package_data=True
)
