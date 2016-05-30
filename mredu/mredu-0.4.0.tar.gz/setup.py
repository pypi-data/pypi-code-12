from setuptools import setup

setup(name='mredu',
      version='0.4.0',
      description='A simple simulator of a system which implements map/reduce paradigm.',
      url='http://github.com/ramonpin/mredu',
      author='ramonpin',
      author_email='ramon.pin@gmail.com',
      license='Apache 2.0',
      packages=['mredu'],
      install_requires=[
        'toolz',
      ],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
      ],
      zip_safe=False)
