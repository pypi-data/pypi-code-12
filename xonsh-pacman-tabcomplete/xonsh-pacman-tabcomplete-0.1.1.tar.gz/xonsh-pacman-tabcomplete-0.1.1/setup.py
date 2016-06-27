from setuptools import setup

long_description = open('README.md').read()

setup(
    name="xonsh-pacman-tabcomplete",
    version="0.1.1",
    license="MIT",
    url="https://github.com/gforsyth/xonsh-pacman-tabcomplete",
    description="pacman tabcomplete support for the Xonsh shell",
    long_description=long_description,
    author="Gil Forsyth",
    author_email="gilforsyth@gmail.com",
    packages=['xontrib'],
    package_dir={'xontrib': 'xontrib'},
    package_data={'xontrib': ['*.xsh']},
    zip_safe=False,
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Environment :: Plugins",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Programming Language :: Python"
    ]
)
