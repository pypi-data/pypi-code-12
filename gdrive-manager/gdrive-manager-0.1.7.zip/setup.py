from setuptools import setup


REQUIRES = [
	"google-api-python-client==1.5.1",
	"oauth2client==2.2.0"
]


setup (
	name='gdrive-manager',
	version='0.1.7',
	author='Bao Nguyen',
	author_email='nlbao95@gmail.com',
	description='Download / upload data using Google Drive APIs.',
	url='https://github.com/nlbao/gdrive-manager',
	license='MIT',
	packages=[
		'bin',
	],
	entry_points = {"console_scripts" : [ "gdrive-manager = bin.gdrive_manager:main"]},
	install_requires=REQUIRES,
)