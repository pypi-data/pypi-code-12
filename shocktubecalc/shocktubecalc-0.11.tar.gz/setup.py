from setuptools import setup

setup(name='shocktubecalc',
      version='0.11',
      description='Simple shock tube calculator',
      url='https://gitlab.com/fantaz/simple_shock_tube_calculator',
      author='Jerko Škifić',
      author_email='jerko.skific@riteh.hr',
      license='MIT',
      packages=['shocktubecalc'],
      classifiers = [
        "Programming Language :: Python :: 3",
        'License :: OSI Approved :: MIT License',
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        'Development Status :: 4 - Beta',
        "Topic :: Scientific/Engineering :: Physics"
       ],
      install_requires=[
          'numpy', 'scipy',
      ],
      zip_safe=False)
