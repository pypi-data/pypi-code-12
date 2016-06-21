from setuptools import setup, find_packages

version = "0.0.2"
name = "fennec"
description = "Fennec is a simple toolbox for statistical analysis."

author = "Amane SUZUKI"
email = "amane.suzu@gmail.com"
url = "https://github.com/amaotone/fennec"

classifiers = [
    "Development Status :: 3 - Alpha",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3 :: Only",
    "Topic :: Scientific/Engineering"
]

install_requires = [
    "pytz",
    "numpy",
    "pandas"
]

setup(
    name=name,
    version=version,
    description=description,
    author=author,
    author_email=email,
    license='MIT',
    url=url,
    packages=find_packages(),
    classifiers=classifiers,
    install_requires=install_requires
)
