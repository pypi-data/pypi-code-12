from setuptools import setup, find_packages

setup(name='linkeddataframe',
      description='Subclass of DataFrame which allows linking to other DataFrames.',
      version='0.0.1',
      author="Peter Kucirek",
      author_email="pkucirek@pbworld.com",
      packages=find_packages(),
      platforms='any',
      url='https://github.com/pbsag/linkeddataframe',
      install_requires=['pandas', 'numpy', 'numexpr'],
      long_description="""
LinkedDataFrame (LDF for short) is a subclass of pandas.DataFrame which implements "chained" attribute access through
pre-specified links. More concisely, LDF is designed to mimic a Python class structure, allowing for "reference" links
to other tables.

The project is hosted at https://github.com/pbsag/linkeddataframe
      """
      )
