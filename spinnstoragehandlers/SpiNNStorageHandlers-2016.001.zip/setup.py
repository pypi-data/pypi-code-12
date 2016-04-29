try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="SpiNNStorageHandlers",
    version="2016.001",
    description="I/O handler classes for SpiNNaker software stack",
    url="https://github.com/SpiNNakerManchester/SpiNNStorageHandlers",
    license="GNU GPLv3.0",
    packages=['spinn_storage_handlers',
              'spinn_storage_handlers.abstract_classes'],
    install_requires=['six']
)
