from setuptools import setup

    
setup(name='rugplot',
      version='0.8.1',
      description='SVG RugPlot Python API',
      long_description=open('README.rst').read(),
      classifiers=[
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Programming Language :: Python :: 2.7',
          'Topic :: Scientific/Engineering :: Information Analysis',
          'Intended Audience :: Science/Research',
          'Topic :: Scientific/Engineering',
      ],
      url='http://github.com/CSB-IG/rugplot',
      author='Rodrigo Garcia',
      author_email='rgarcia@inmegen.gob.mx',
      license='GPLv3',
      packages=['rugplot'],
      install_requires=[ 'svgwrite' ],
      zip_safe=False)
