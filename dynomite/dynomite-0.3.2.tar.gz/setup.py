from setuptools import setup
import os

# Try to load version from local version file
version_filename = 'VERSION'
setup_path = os.path.dirname(os.path.realpath(__file__))
version_path = os.path.join(setup_path, version_filename)
version_file = open(version_path)
version = version_file.read().strip()

# Configure the distribution
setup(name='dynomite',
      version=version,
      description='Dynomite',
      package_dir={'dynomite': 'dynomite',
                   'dynomite.s3': 'dynomite/s3',
                   'dynomite.dynamodb': 'dynomite/dynamodb'},
      scripts=['bin/dynamodbctl', 'bin/s3ctl'],
      packages=['dynomite',
                'dynomite.dynamodb',
                'dynomite.s3'],
      package_data={'dynomite':
                    ['dynamodb/templates/backup_pipeline_def.json',
                     'templates/bucket_policy.json',
                     'dynamodb/templates/restore_pipeline_def.json',
                     'dynamodb/templates/data_pipeline_default_resource_role.json',
                     'dynamodb/templates/data_pipeline_default_role.json',
                     'dynamodb/templates/data_pipeline_default_resource_role_policy.json',
                     'dynamodb/templates/data_pipeline_default_role_policy.json',
                     'templates/user_policy.json']},
      url='https://github.com/socotra/dynomite',
      download_url='https://github.com/socotra/dynomite/tarball/0.1.0',
      maintainer='Chris Antenesse',
      maintainer_email='chris.antenesse@socotra.com',
      license='all rights reserved',
      long_description=open('README.md', 'rt').read(),
      install_requires=['boto>=2.38.0'])
