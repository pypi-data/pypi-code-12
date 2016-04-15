from setuptools import setup, find_packages

setup(name='esgf-test-suite',
      version='0.2.3',
      description='Nose scripts for ESGF integration test and validation',
      url='http://github.com/ESGF/esgf-test-suite',
      author='Nicolas Carenton',
      author_email='nicolas.carenton@ipsl.jussieu.fr',
      license='IPSL',
      packages=find_packages(),
      install_requires=[
          'nose',
          'pyOpenSSL==0.13.1',
	  'MyProxyClient',
	  'requests',
	  'lxml',
	  'splinter',
      ],
      zip_safe=False,
      include_package_data=True)
