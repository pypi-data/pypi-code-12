from setuptools import setup, find_packages

setup(
    name='cloud_lib',
    version='1.1.9',
    description='Cloud Service Library',
    long_description='https://pypi.python.org/pypi/cloud_lib',
    url='https://github.com/Akira-Taniguchi/cloud_lib',
    author='AkiraTaniguchi',
    author_email ='dededededaiou2003@yahoo.co.jp',
    packages=find_packages(),
    license='MIT',
    keywords='amazon google cloud bigquery storage s3 ec2',
    classifiers=[
      'Development Status :: 5 - Production/Stable',
      'Programming Language :: Python :: 2.7',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: MIT License'
    ],
    install_requires=['boto3==1.2.2', 'google-api-python-client==1.5.0']
)
