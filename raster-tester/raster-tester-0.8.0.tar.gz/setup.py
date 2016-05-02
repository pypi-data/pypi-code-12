from codecs import open as codecs_open
from setuptools import setup, find_packages


# Get the long description from the relevant file
with codecs_open('README.rst', encoding='utf-8') as f:
    long_description = f.read()


setup(name='raster-tester',
      version='0.8.0',
      description=u"Tools for testing rasters",
      long_description=long_description,
      classifiers=[],
      keywords='',
      author=u"Camilla Mahon",
      author_email='camilla@mapbox.com',
      url='https://github.com/mapbox/raster-tester',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'click',
          'rasterio'
      ],
      extras_require={
          'test': ['pytest', 'pytest-cov', 'codecov'],
      },
      entry_points="""
      [console_scripts]
      raster-tester=raster_tester.scripts.cli:cli
      """
      )
