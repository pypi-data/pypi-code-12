from setuptools import setup

setup(name='sjc_funniest',
      version='0.2',
      description='The funniest joke in the world',
      url='http://github.com/storborg/funniest',
      author='Flying Circus',
      author_email='flyingcircus@example.com',
      license='MIT',
      packages=['sjc_funniest'],
     install_requires=[
          'markdown',
      ],
      zip_safe=False)
