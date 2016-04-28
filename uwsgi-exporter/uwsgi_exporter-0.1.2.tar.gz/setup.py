#!/usr/bin/env python3
import os
from setuptools import setup

here = os.path.dirname(os.path.abspath(__file__))


def get_long_description():
    with open(os.path.join(here, "README.MD")) as f:
        return f.read()


setup(name="uwsgi_exporter",
      version="0.1.2",
      description="Prometheus uwsgi stats exporter",
      long_description=get_long_description(),
      author="Shevchenko Vitaliy",
      author_email="vetal4444@gmail.com",
      scripts=("uwsgi_exporter.py",),
      install_requires=("requests-unixsocket", "prometheus_client"),
      classifiers=(
          "Programming Language :: Python :: 3.3",
          "Programming Language :: Python :: 3.4",
          "Programming Language :: Python :: 3.5",
      ),
      url="https://bitbucket.org/semanticapps/uwsgi_exporter/",
      keywords="uwsgi export stats prometheus"
      )
