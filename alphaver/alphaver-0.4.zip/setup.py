from setuptools import setup
setup(
  name = 'alphaver',
  packages = ['alphaver'], # this must be the same as the name above
  version = '0.4',
  description = 'Alpha version for cg_acc',
  author = 'Unknown',
  author_email = 'avikalp22@gmail.com',
  url = 'https://github.com/Avikalp7/CG-Accumulator', # use the URL to the github repo
  # download_url = 'https://github.com/Avikalp7/Golden-Shoe/tarball/0.1', # I'll explain this in a second
  keywords = ['testing', 'cg_acc', 'example'], # arbitrary keywords
  
  license = 'MIT',
  
  classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
    ],

    install_requires=['requests', 'bs4', 'prettytable'],
)