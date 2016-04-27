from setuptools import setup, find_packages

version = "0.9.0"

setup(name="pypgqueue",
      version=version,
      description="A job queue based on PostgreSQL's listen/notify features",
      author="Trey Cucco",
      author_email="fcucco@gmail.com",
      url="https://github.com/treycucco/pypgq",
      download_url="https://github.com/treycucco/pypgq/tarball/master",
      packages=["pypgq"],
      package_data={"pypgq": ["ddl.sql"]},
      install_requires=[
        "bidon >= 1.0.4",
        "psycopg2"
      ],
      classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3 :: Only"
      ],
      license="BSD",
      platforms="any")
