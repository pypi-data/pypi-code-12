#!/usr/bin/env python

from distutils.core import setup

setup(name='aes-vial',
      version='0.1.0',
      description='A simple wrapper for AES CTR mode.',
      author='Peter Badida',
      author_email='keyweeusr@gmail.com',
      url='https://github.com/KeyWeeUsr/Vial',
      download_url='https://github.com/KeyWeeUsr/Vial/tarball/0.1.0',
      packages=['vial'],
      classifiers=[
          'Topic :: Security :: Cryptography',
          'License :: OSI Approved :: MIT License',
      ],
      keywords=['security', 'cryptography', 'wrapper', 'aes', 'ctr'],
      license="License :: OSI Approved :: MIT License",
      )
