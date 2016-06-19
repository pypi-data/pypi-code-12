from distutils.core import setup

setup(
    name='dhcpctl',
    version='0.1.0',
    packages=['dhcpctl'],
    install_requires=['isc-dhcp-leases', 'arghandler', 'distro', 'tabulate'],
    license='MIT',
    url='https://github.com/MartijnBraam/dhcpctl',
    author='Martijn Braam',
    author_email='martijn@brixit.nl',
    description='A python command line tool for managing and viewing dhcp leases',
    entry_points={
        'console_scripts': [
            'dhcpctl = dhcpctl.main'
        ]
    },

)
