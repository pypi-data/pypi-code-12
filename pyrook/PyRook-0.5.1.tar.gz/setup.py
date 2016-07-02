from setuptools import setup, find_packages

from PyRook import __version__

setup(
        name="PyRook",
        version=__version__,
        description="A standalone client for RookChat",
        url="https://sentynel.com/project/PyRook",
        author="Sam Lade",
        author_email="pyrook@sentynel.com",
        license="Public Domain",
        classifiers=[
            "Development Status :: 4 - Beta",
            "Environment :: X11 Applications :: Qt",
            "License :: Public Domain",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3 :: Only",
            "Programming Language :: Python :: 3.3",
            "Programming Language :: Python :: 3.4",
            "Programming Language :: Python :: 3.5",
            "Topic :: Communications :: Chat",
        ],
        keywords="rookchat",
        packages=["PyRook", "PyRook.Importer"],
        # we require PyQt4 or PyQt5 as well, but we can't usefully specify
        # those as requirements to setuptools
        install_requires=["lxml",],
        package_data={
            "PyRook": ["data/pyrook_logo.svg", "data/pyrook_logo.ico",
                "data/PyRook.desktop", "data/en_US.dic", "data/en_US.aff"],
        },
        entry_points={
            "console_scripts": ["pyrook_console = PyRook.PyRook:main"],
            "gui_scripts": ["pyrook = PyRook.PyRook:main"],
        },
)
