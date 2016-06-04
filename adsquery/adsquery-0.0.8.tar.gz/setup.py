from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='adsquery',
      version='0.0.8',
      description='Query the ADS using python',
      long_description=readme(),
      url='https://github.com/cphyc/adsquery',
      author='cphyc (Corentin Cadiou)',
      author_email='contact@cphyc.me',
      license='MIT',
      packages=['adsquery'],
      install_requires=[
          'requests',
          'ads',
          'tqdm'
      ],
      zip_safe=False,
      scripts=['bin/adsquery'])
