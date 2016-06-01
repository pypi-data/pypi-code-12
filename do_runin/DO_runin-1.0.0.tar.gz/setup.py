from setuptools import setup

with open("README.md", "rb") as f:
    long_descr = f.read().decode('utf-8')

setup(
    name = "DO_runin",
    packages = ["runin"],
    install_requires = ['requests'],
    entry_points = {
        "console_scripts": ['runin = runin.runin:main']
        },
    version = "1.0.0",
    description = "A tool that starts a DigitalOcean droplet in a given region and runs a given command, displaying the output. Opens a shell if requested. Destroys the droplet upon command completion or shell closure.",
    long_description = long_descr,
    author = "Steven Smith",
    author_email = "stevensmith.ome@gmail.com",
    license = "MIT",
    url = "https://github.com/blha303/DO-runin",
    classifiers = [
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",
        ]
    )
