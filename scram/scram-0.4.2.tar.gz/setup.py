'''
Created on 27 May 2016

@author: steve
'''
from setuptools import setup

setup(name='scram',
      version='0.4.2',
      description=' Small Complementary RnA Mapper',
      url='https://github.com/Carroll-Lab/scram',
      author='Stephen Fletcher',
      author_email='s.fletcher@uq.edu.au',
      license='MIT',
      packages=['scram_modules'],
      classifiers=[
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    'Development Status :: 4 - Beta',
    'Intended Audience :: Science/Research',
    # Indicate who your project is intended for

    'Topic :: Scientific/Engineering :: Bio-Informatics',

    # Pick your license as you wish (should match "license" above)
     'License :: OSI Approved :: MIT License',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 2.7'],
      install_requires=['numpy','matplotlib'],
      scripts=['scram_modules/scram',
      'scram_modules/analysis.py',
      'scram_modules/align_srna.py',
      'scram_modules/analysis_helper.py',
      'scram_modules/cdp.py',
      'scram_modules/den.py',
      'scram_modules/dna.py',
      'scram_modules/plot_reads.py',
      'scram_modules/post_process.py',
      'scram_modules/ref_seq.py',
      'scram_modules/srna_seq.py',
      'scram_modules/write_to_file.py',
      ],
      zip_safe=False)