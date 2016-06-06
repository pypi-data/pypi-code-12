from distutils.core import setup

setup(
	name='HumanRandom',
	version='1.1b',
	description='Pseudo-randomize things in a way that feels human',
	author='katacarbix',
	author_email='me@katacarbix.xyz',
	url='https://github.com/katacarbix/HumanRandom',
	license="WTFPL",
	packages=['HumanRandom'],
	keywords='human random shuffle ux development',
	install_requires=['difflib', 'random'],

	classifiers=[
	    'Development Status :: 4 - Beta',
	    'Intended Audience :: Developers',
	    'Topic :: Software Development :: Libraries',
	     'License :: Public Domain',
	    'Programming Language :: Python :: 2'
	]
)
