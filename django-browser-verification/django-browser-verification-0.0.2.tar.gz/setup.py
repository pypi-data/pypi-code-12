from setuptools import setup, find_packages

setup(
    name="django-browser-verification",
    version="0.0.2",
    author="John Leith",
    author_email="john@iglobalstores.com",
    packages=find_packages(),
    install_requires=(
        'six', 'user-agents'
    ),
    scripts=[],
    include_package_data=True,
    zip_safe=False,
)
