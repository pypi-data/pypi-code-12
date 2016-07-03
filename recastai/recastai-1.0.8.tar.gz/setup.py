from setuptools import setup, find_packages
from codecs import open


# Get the long description from the README file
with open('README.md', 'r', 'utf-8') as f:
  readme = f.read()

setup(
    name="recastai",
    version="1.0.8",
    packages=find_packages(),
    description="Recast.AI official SDK for python",
    long_description=readme,
    author="Paul Renvoise",
    author_email="paul.renvoise@recast.ai",
    url="https://github.com/RecastAI/sdk-python",
    license="MIT",
    keywords="recastai bot nlp")
