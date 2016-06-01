from distutils.core import setup

setup(
	name='hatchlib',
	version='0.5.9',
	description='Hatch Alpha algorithm library',
	author='Lia',
	author_email='inoriy.sh@gmail.com',
	
	packages=['hatchlib','hatchlib.dynamic','hatchlib.encoding','hatchlib.factorize','hatchlib.math','hatchlib.search','hatchlib.shuffle','hatchlib.sort'],
	
	url='https://github.com/LiaSL/hatchlib',
	download_url='https://github.com/LiaSL/hatchlib/tarball/pypi',
	keywords=['algorithms','library'],
	
	classifiers=[]
)