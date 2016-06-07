from setuptools import setup

from arya.build.core import get_attrs


setup(
    setup_requires=['pbr'],
    **get_attrs()
)
