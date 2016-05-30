from setuptools import setup

setup(
  name = 'sftp_s3_sync',
  packages = ['sftp_s3_sync'], # this must be the same as the name above
  version = '2.0.1',
  description = 'A python sftp and s3 syncing library',
  author = 'Partha',
  author_email = 'parthasaradhi1992@gmail.com',
  url = 'https://github.com/parthz/sftp-s3-sync', 
  download_url = 'https://github.com/parthz/sftp-s3-sync/tarball/0.1', 
  keywords = ['ftp sync s3', 'sftp sync s3'], 
  classifiers = [],
  install_requires=[
        "boto",
        "paramiko"
    ],
  zip_safe=False)
