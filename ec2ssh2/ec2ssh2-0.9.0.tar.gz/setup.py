from setuptools import setup

version_path = 'ec2ssh2/version.py'

exec(open(version_path).read())

setup(
    name="ec2ssh2",
    zip_safe=True,
    version=VERSION,
    description="tag-based ec2 instance SSH with environment variable configuration",
    url="http://github.com/scivey/ec2ssh2",
    maintainer="Scott Ivey",
    maintainer_email="scott.ivey@gmail.com",
    packages=['ec2ssh2'],
    package_dir={'ec2ssh2': 'ec2ssh2'},
    install_requires=['boto3>=1.3.1']
)
