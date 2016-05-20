from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='yac',
      version='0.965',
      description='yac portable services',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Text Processing :: Linguistic',
      ],
      keywords='service cloudformation aws ecs docker',
      url='https://bitbucket.org/thomas_b_jackson/yac',
      author='Thomas Jackson',
      author_email='thomas.b.jackson@gmail.com',
      license='MIT',
      packages=['yac'],
      scripts=['yac/bin/yac'],
      include_package_data=True,
      install_requires=[
          'boto3',
          'boto',
          'redis',
          'fakeredis',
          'docker-py',
          'SQLAlchemy',
          'pg8000'      
      ],
      zip_safe=False)
