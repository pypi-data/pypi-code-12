from setuptools import setup

setup(name='landsatbuoycalib',
      version='0.1',
      description='Calculates and compares the radiance of a thermal LANSAT scene to the "ground truthradiance as measured by a NOAA buoy.',
      url='https://github.com/ndileas/Landsat-Buoy-Calibration',
      author='Nathan Dileas',
      author_email='nid4986@rit.edu',
      license='MIT',
      packages=['landsatbuoycalib'],
      zip_safe=False)