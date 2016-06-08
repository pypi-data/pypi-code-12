from distutils.core import setup

with open('version.txt', 'r') as f:
  version = f.read()
  version = str(float(version) + 0.01)
with open('version.txt', 'w') as f:
  f.write(version)

setup(
  name = 'ssh2',
  scripts = ['bin/ssh2'],
  version = version,
  description = 'Simplifying EC2 ssh\'ing',
  long_description = open('README.rst', 'rt').read(),
  author = 'Soheil Yasrebi',
  author_email = 'ysoheil@gmail.com',
  url = 'https://github.com/soheil/ssh2',
  keywords = ['ssh', 'ec2', 'aws'],
  classifiers = [],
)