from distutils.core import setup

setup(
    # Application name:
    name="VmMonProbe",

    # Version number (initial):
    version="0.1.2",

    # Application author details:
    author="Panos Karkazis",
    author_email="pkarkazis@synelixis.com",

    # Packages
    packages=["vm_mon_probe"],

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="http://pypi.python.org/pypi/syn_vm_probe_v010/",

    #
    license="LICENSE.txt",
    description="Monitoring probe gathers data from VM's linux kernel ",

    # long_description=open("README.txt").read(),

    # Dependent packages (distributions)
    #install_requires=[
    #    "flask",
    #],
)