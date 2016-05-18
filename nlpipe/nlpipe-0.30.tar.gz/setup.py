#!/usr/bin/env python

from distutils.core import setup

setup(
    name="nlpipe",
    version="0.30",
    description="Simple NLP Pipelinining using Elastic and Celery",
    author="Wouter van Atteveldt",
    author_email="wouter@vanatteveldt.com",
    packages=["nlpipe", "nlpipe.scripts", "nlpipe.modules"],
    keywords = ["NLP", "pipelining"],
    download_url="https://github.com/amcat/nlpipe/tarball/0.1",
    classifiers=[
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Topic :: Text Processing",
    ],
    install_requires=[
        "celery>=3.0.0",
        "elasticsearch",
        "KafNafParserPy",
        "pynlpl",
        "corenlp-xml>=1.0.3",
        "unidecode",
    ],
    dependency_links=[
        "https://github.com/vanatteveldt/corenlp-xml-lib/tarball/master#egg=corenlp-xml-1.0.3"        
    ]
)
