#!/usr/bin/env python
#coding:utf-8
"""
  Author:  Yeison Cardona --<yeison.eng@gmail.com>
  Purpose:
  Created: 13/02/16
"""

from setuptools import setup, find_packages
import os

#Compile mse.c
file = os.path.join("pymse", "mse", "mse")
os.system("gcc -o {0} -O {0}.c -lm".format(file))
#os.chdir(os.path.dirname(__file__))

setup(name = "pymse",
      version = "0.1.9",
      packages = find_packages(),
      include_package_data=True,
      description = "Calculates multiscale entropy (MSE) of one or multiple data sets.",
      description_file = "README.md",

      author = "M. Costa",
      author_email = "mcosta@fsa.harvard.edu",
      maintainer = "Yeison Cardona",
      maintainer_email = "yeison.eng@gmail.com",

      url = "http://www.physionet.org/",
      download_url = "https://bitbucket.org/yeisoneng/pymse/downloads",

      license = "BSD 3-Clause",
      install_requires = ["numpy"],

      keywords = "mse",

      classifiers=[#list of classifiers in https://pypi.python.org/pypi?:action=list_classifiers
                   "Programming Language :: Python",
                   ],

      #scripts = [
          #"mse/mse", # compiled mse
          #],

      zip_safe = False

      )
