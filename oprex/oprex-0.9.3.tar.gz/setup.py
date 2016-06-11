from distutils.core import setup

setup(
    name='oprex',
    packages = ['oprex'],
    version='0.9.3',
    author='Ron Panduwana',
    author_email='panduwana@gmail.com',
    include_package_data=True,
    url='https://github.com/rooney/oprex',
    download_url='https://github.com/rooney/oprex/tarball/0.9.3',
    license='LICENSE',
    description='A more-readable alternative syntax for regex',
	keywords = ['regex'],
	classifiers = ['Development Status :: 4 - Beta'],
    install_requires=[
		'ply>=3.8',
		'regex==2016.6.5',
    ],
)
