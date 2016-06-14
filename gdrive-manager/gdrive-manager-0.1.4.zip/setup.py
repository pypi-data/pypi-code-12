from setuptools import setup


REQUIRES = [
	"google-api-python-client==1.5.1",
	"oauth2client==2.2.0"
]


setup (
	name='gdrive-manager',    				       # This is the name of your PyPI-package.
	version='0.1.4',                               # Update the version number for new releases
	scripts=['gdrive-manager/gdrive-manager.py'],  # The name of your scipt, and also the command you'll be using for calling it
    packages=[
        'gdrive-manager',
    ],
	author='Bao Nguyen',
	author_email='nlbao95@gmail.com',
	description='Download / upload data using Google Drive APIs.',
	url='https://github.com/nlbao/gdrive-manager',
	license='MIT',
	install_requires=REQUIRES,
)