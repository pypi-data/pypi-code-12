"""Gatekeeper service independent code."""
from pip.req import parse_requirements
from setuptools import setup, find_packages


dependencies = parse_requirements('requirements.txt', session=False)
reqs = [str(ir.req) for ir in dependencies]
setup(
    name='gakp-pylib',
    version='0.2.5',
    url='https://gitlab.com/gakp/pylib.git',
    author='gatekeeper',
    author_email='arewa.olakunle@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=reqs,
    long_description=open("README.md").read()
)
