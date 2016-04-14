from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='biopantograph',
      version='0.3.1',
      description='Pantograph is a toolbox for the reconstruction, curation and validation of metabolic models.',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
      ],
      keywords='pantograph metabolic model reconstruction',
      url='http://pathtastic.gforge.inria.fr',
      author='Nicolas Loira',
      author_email='nloira@gmail.com',
      license='GPLv2',
      packages=['biopantograph'],
      install_requires=['python-libsbml','requests'],
      entry_points={'console_scripts': [ 
	      'ptg_addbiggreactions=biopantograph.ptg_addbiggreactions:main', 
	      'ptg_projector=biopantograph.ptg_projector:main',
	      'ptg_curateSBML=biopantograph.ptg_curateSBML:main',
	      'ptg_inparanoid2rel=biopantograph.ptg_inparanoid2rel:main',
	      'ptg_omcl2rel=biopantograph.ptg_omcl2rel:main',
	      ], },
      include_package_data=True,
      scripts=['bin/pantograph']
      )
