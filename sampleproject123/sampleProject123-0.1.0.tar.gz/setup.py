from distutils.core import setup
with open("README.rst") as f:
	readme=f.read()
setup(
	#Application Name
	name="sampleProject123",
	#version
	version="0.1.0",
	#Application author details:
	author="ashwinraju101",
	author_email="ashwinraju101@gmail.com",
	py_modules=["my_package"],
	include_package_data=True,
	description="A faster way to read image from bioformats",
	long_description=readme,
	install_requires=["bioformats","javabridge","numpy","pytables"]
	)
