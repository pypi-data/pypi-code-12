"""
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  This file is part of the Smart Developer Hub Project:
    http://www.smartdeveloperhub.org

  Center for Open Middleware
        http://www.centeropenmiddleware.com/
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  Copyright (C) 2015 Center for Open Middleware.
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

            http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
"""

__author__ = 'Fernando Serena'

from setuptools import setup, find_packages

setup(
    name="Fragment-Service-Provider",
    version="0.1.0",
    author="Fernando Serena",
    author_email="fernando.serena@centeropenmiddleware.com",
    description="A library for making web services built on the SDH Fragment Provider",
    license="Apache 2",
    keywords=["linked-data", "path", "ontology", "plan"],
    url="https://github.com/smartdeveloperhub/fragment-service-provider",
    download_url="https://github.com/smartdeveloperhub/fragment-service-provider/tarball/0.0.8",
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['sdh', 'sdh.fragments'],
    install_requires=['flask', 'rdflib', 'Agora-Stoa-Client', 'SPARQLWrapper==1.7.2'],
    classifiers=[]
)
