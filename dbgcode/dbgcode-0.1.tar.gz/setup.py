from setuptools import setup, find_packages

setup(name="dbgcode",
      version="0.1",
      description="write debug code with confidence",
      author="Ali Faki",
      author_email="alifaki077@gmail.com",
      license="MIT",
      packages=find_packages(),
      scripts=["bin/dbgcode"]
      )
