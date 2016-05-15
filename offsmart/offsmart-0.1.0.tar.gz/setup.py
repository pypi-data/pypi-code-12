from setuptools import setup

setup(name='offsmart',
      version='0.1.0',
      description='Saves data locally until there is internet access.',
      author='Joao Tavares',
      author_email='veroight@gmail.com',
      install_requires = ['storm>=0.20'],
      license='MIT',
      packages=['offsmart'],
      zip_safe=False,
       classifiers=[
        'Development Status :: 2 - Pre-Alpha',
    ])
