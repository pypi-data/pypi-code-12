# vim: set fileencoding=utf-8 :
from setuptools import setup, find_packages

setup(
    name="capillary",
    version="0.0.1",
    author="Domen Kožar, Aaron McMillin",
    author_email="aaron@mcmillinclan.org",
    description="Declarative workflows for celery.",
    packages=find_packages("."),

    url="https://github.com/celery-capillary/capillary",


    install_requires=[
        'networkx',
        'venusian',
    ],
)
