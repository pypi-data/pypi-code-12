from setuptools import setup
setup(
    name = "pytronix",
    version = "0.9",
    packages = [ 'pytronix' ],
    package_dir = { 'pytronix':'' },
    package_data = { '': ['*.txt','*.md'] },
    install_requires = [ 'telepythic >= 1.4' ],
    
    # metadata for upload to PyPI
    author = "Martijn Jasperse",
    author_email = "m.jasperse@gmail.com",
    description = "A python project to easily and rapidly download data from TekTronix DSOs",
    long_description = "This project provides the ability to quickly downloading scope data from a TekTronix digital oscilloscope using the telnet interface.",
    license = "BSD",
    keywords = "TekTronix TDS DPO MSO CRO scope HDF5",
    url = "https://bitbucket.org/martijnj/pytronix",
)
