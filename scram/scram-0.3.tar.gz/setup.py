from setuptools import setup

setup(name='scram',
      version='0.3',
      description=' Small Complementary RnA Mapper',
      url='https://github.com/Carroll-Lab/scram',
      author='Stephen Fletcher',
      author_email='s.fletcher@uq.edu.au',
      license='MIT',
      packages=['scram'],
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
      scripts=['scram/scram',
      'scram/analysis.py',
      'scram/align_srna.py',
      'scram/analysis_helper.py',
      'scram/cdp.py',
      'scram/den.py',
      'scram/dna.py',
      'scram/plot_reads.py',
      'scram/post_process.py',
      'scram/ref_seq.py',
      'scram/srna_seq.py',
      'scram/write_to_file.py',
      ],
      zip_safe=False)
