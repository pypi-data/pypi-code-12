from setuptools import setup, find_packages

version = "1.0.0"

setup(name="bidon",
      version=version,
      description="A simple, easy to use, and flexible data handling library",
      author="Trey Cucco",
      author_email="fcucco@gmail.com",
      url="https://github.com/treycucco/bidon",
      download_url="https://github.com/treycucco/bidon/tarball/master",
      packages=["bidon",
                "bidon.db",
                "bidon.db.access",
                "bidon.db.core",
                "bidon.db.model",
                "bidon.experimental",
                "bidon.spreadsheet",
                "bidon.util"],
      classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3 :: Only"],
      license="BSD",
      platforms="any")
