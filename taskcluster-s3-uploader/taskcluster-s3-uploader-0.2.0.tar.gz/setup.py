import os
from setuptools import setup, find_packages

# Utility function to read the README file.
def read(fname):
        return open(os.path.join(os.path.dirname(__file__), fname)).read()

required = [
    'boto3',
    'taskcluster'
]

setup(
    name='taskcluster-s3-uploader',
    version='0.2.0',
    packages=find_packages(),
    install_requires=required,
    tests_require=required,
    # Meta-data for upload to PyPI
    author='Armen Zambrano G.',
    author_email='armenzg@mozilla.com',
    description='Upload files to S3 with your TaskCluster authentication',
    long_description=read('README.md'),
    license='MPL',
    url='https://github.com/armenzg/treeherder_submitter',
)
