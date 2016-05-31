from distutils.core import setup

setup(name='lcspotter',
      description='Simulate light curves of spotted stars using Gaussian processes.',
      version='0.1.0',
      author='Rodrigo F. Diaz',
      author_email='rodrigo.diaz@unige.ch',
      url='',
      package_dir={'':'src'},
      scripts=['bin/lcspotter'],
      py_modules=['spotlc'],      
      requires=['numpy', 'scipy']
      )
