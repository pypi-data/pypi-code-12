from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Education",
    "Intended Audience :: Science/Research",
    "Natural Language :: English",
    "License :: OSI Approved :: BSD License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.5",
    "Topic :: Scientific/Engineering :: Physics", 
]

setup(name='positronium',
      version='0.1.7',
      description='python tools pertaining to positronium',
      url='https://github.com/PositroniumSpectroscopy/positronium',
      author='Adam Deller',
      author_email='adam.deller1@gmail.com',
      license='BSD',
      packages=['positronium'],
      install_requires=[
          'scipy>0.14', 'numpy>1.10',
      ],
      include_package_data=True,
      classifiers=CLASSIFIERS,
      zip_safe=False)
