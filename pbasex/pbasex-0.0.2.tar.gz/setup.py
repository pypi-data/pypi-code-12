from setuptools import setup

if __name__ == '__main__':
	setup(
		  name='pbasex',
		  packages=['pbasex'],
		  install_requires=['numpy','h5py','dill'],
		  version='0.0.2',
		  description='pBASEX implementation without polar rebinning.',
		  url='https://github.com/e-champenois/CPBASEX',
		  author='Elio Champenois',
		  author_email='elio.champenois@gmail.com',
		  license='MIT',
		  zip_safe=False
		  )