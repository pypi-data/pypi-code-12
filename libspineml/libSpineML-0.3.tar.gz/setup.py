from distutils.core import setup
import setuptools
 
setup(name = "libSpineML",
      version = "0.3",
      description = "Python bindings for the SpineML specifications",
      author = "Adam Tomkins",
      author_email = "a.tomkins@sheffield.ac.uk",
      url='http://github.com/AdamRTomkins/libSpineML',
      packages=["libSpineML"],
      install_requires=[
          'lxml >= 3.3.0'
      ],
      setup_requires=['pytest-runner'],
      tests_require=['pytest']
      )
