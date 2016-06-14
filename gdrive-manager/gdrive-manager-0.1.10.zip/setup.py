from setuptools import setup


REQUIRES = [
	"google-api-python-client==1.5.1",
	"oauth2client==2.2.0"
]


setup (
	name='gdrive-manager',
	version='0.1.10',
	author='Bao Nguyen',
	author_email='nlbao95@gmail.com',
	description='Download / upload data using Google Drive APIs.',
	url='https://github.com/nlbao/gdrive-manager',
	license='MIT',
	packages=[
		'gdrive_manager',
	],
	# data_files = [
	# 	('gdrive_manager', ['gdrive_manager/client_secret.json'])
	# ],

	package_dir={'gdrive_manager': 'gdrive_manager'},
	package_data={'gdrive_manager': ['client_secret.json']},

	entry_points = {"console_scripts" : [ "gdrive-manager = gdrive_manager.gdrive_manager:main"]},
	install_requires=REQUIRES,
)