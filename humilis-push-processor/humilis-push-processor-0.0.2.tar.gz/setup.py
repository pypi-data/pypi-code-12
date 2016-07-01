"""Setuptools entrypoint."""

import codecs
import os

from setuptools import setup, find_packages

from humilis_push_processor import __version__

dirname = os.path.dirname(__file__)

long_description = (
    codecs.open(os.path.join(dirname, "README.rst"), encoding="utf-8").read() + "\n" +   # noqa
    codecs.open(os.path.join(dirname, "AUTHORS.rst"), encoding="utf-8").read() + "\n" +  # noqa
    codecs.open(os.path.join(dirname, "CHANGES.rst"), encoding="utf-8").read()
)

setup(
    name="humilis-push-processor",
    include_package_data=True,
    package_data={"": ["*.j2", "*.yaml"]},
    packages=find_packages(include=['humilis_push_processor',
                                    'humilis_push_processor.*']),
    version=__version__,
    author="German Gomez-Herrero, FindHotel and others",
    author_email="data@findhotel.net",
    url="http://github.com/humilis/humilis-push-processor",
    license="MIT",
    description="Humilis push event processor plugin",
    long_description=long_description,
    install_requires=["humilis>=0.4.1"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2"
    ],
    zip_safe=False,
    entry_points={
        "humilis.layers": [
            "push-processor="
            "humilis_push_processor.plugin:get_layer_path"]}
)
