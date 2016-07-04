from setuptools import setup, find_packages
setup(name="ssh-tool", 
	author="arron",
	author_email="fsxchen@gmail.com",
	version="0.0.2",
    	package_data = {'':['*.*']},
	packages=find_packages(),
    	py_modules=['ssh-tool'],
    scripts=['bin/sshtool.py']
)
