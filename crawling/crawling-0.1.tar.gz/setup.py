from setuptools import setup, find_packages

setup(
    name="crawling",
    version="0.1",
    author="pandada8",
    author_email="pandada8@gmail.com",
    packages=find_packages(),
    license="MIT",
    install_requires=["aiohttp >= 0.20"],
    entry_points={
        "console_scripts": ["crawling=crawling.cli:main"]
    },
    description="A tiny spider suite",
    url="https://github.com/pandada8/crawling"
)
