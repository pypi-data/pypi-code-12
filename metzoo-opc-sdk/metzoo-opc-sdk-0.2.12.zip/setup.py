from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='metzoo-opc-sdk',
      version='0.2.12',
      description='OPC SDK for Metzoo',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
      ],
      data_files=[('metzoo_opc_config', ['config-template.yaml'])],
      keywords='metzoo monitoring metric opc',
      url='https://bitbucket.org/edrans/metzoo-opc-sdk',
      author='Edrans',
      author_email='info@edrans.com',
      license='MIT',
      packages=['metzoo_opc'],
      install_requires=['metzoo-python-sdk', 'pyyaml', 'pyro'],
      zip_safe=False)
