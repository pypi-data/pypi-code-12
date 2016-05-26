from distutils.core import setup

setup(
    name='srxpolicysearch',
    version='0.0.5',
    packages=['srxpolicysearch'],
    url='https://github.com/lampwins/srxpolicysearch',
    license='MIT',
    author='John Anderson',
    author_email='lampwins@gmail.com',
    description='Search security policy on the Juniper SRX platform',
    install_requires=['paramiko']
)
