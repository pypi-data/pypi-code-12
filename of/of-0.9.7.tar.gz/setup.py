
"""
Created on Apr 8, 2016

@author: Nicklas Boerjesson
"""

from setuptools import setup

import sys, os

from of import __release__

if __name__ == "__main__":
    setup(
        name="of",
        version=__release__,
        description="The Optimal Framework is the fastest path to building any modern multi-user system",
        author="Nicklas Boerjesson",
        author_email="nicklas_attheold_optimalbpm.se",
        maintainer="Nicklas Boerjesson",
        maintainer_email="nicklas_attheold_optimalbpm.se",
        install_requires=["pymongo", "jsonschema", "decorator", "requests", "cherrypy", "pycrypto", "ws4py", "urllib3"],
        long_description="""The Optimal Framework is a turnkey, Python-based development framework.\n
        It starts off with a running server, a MongoDB backend and all baseline features of any multiuser system.""",
        url="https://github.com/OptimalBPM/of",
        packages=["of", "of.broker", "of.broker.cherrypy_api", "of.broker.examples", "of.broker.examples.partial", "of.broker.testing", "of.broker.lib", "of.broker.lib.messaging", "of.broker.ui", "of.broker.ui", "of.common",
                  "of.common.messaging", "of.common.queue", "of.common.security", "of.schemas"],
        package_data = {
            # If any package contains *.md, *.json, *.txt or *.xml, *.sql files, include them:
            "": ["*.md", "*.json", "*.txt", "*.xml", "*.sql", "*.html"]
        },
        license="BSD")
