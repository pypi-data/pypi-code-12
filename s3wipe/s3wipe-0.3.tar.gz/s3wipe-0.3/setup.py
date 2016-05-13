from distutils.core import setup
setup(
  name = 's3wipe',
  packages = ['s3wipe'],
  version = '0.3',
  description = 'Rapid AWS S3 bucket delete tool',
  author = 'Eric Schwimmer',
  author_email = 'git@nerdvana.org',
  url = 'https://github.com/eschwim/s3wipe',
  download_url = 'https://github.com/eschwim/s3wipe/tarball/0.3', 
  keywords = ['aws', 's3', 'bucket', 'delete', 's3nuke'], 
  classifiers = [],
  scripts=['s3wipe/s3wipe'],
)
