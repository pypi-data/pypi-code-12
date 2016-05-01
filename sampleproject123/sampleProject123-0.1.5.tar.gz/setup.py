from setuptools import setup,find_packages
with open("README.rst") as f:
	readme=f.read()
setup(
	#Application Name
	name="sampleProject123",
	#version
	version="0.1.5",
	#Application author details:
	author="ashwinraju101",
	author_email="ashwinraju101@gmail.com",
	py_modules=["my_package"],
	
	description="A faster way to read image from bioformats",
	long_description=readme,
	install_requires=["python-bioformats","numpy","h5py","cython","numexpr","javabridge","blosc","tables",]
	)
