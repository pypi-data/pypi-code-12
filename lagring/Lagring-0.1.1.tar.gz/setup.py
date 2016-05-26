from setuptools import setup

setup(
    name="Lagring",
    version="0.1.1",
    author="Lenar Imamutdinov",
    author_email="lenar.imamutdinov@gmail.com",
    packages=["lagring"],
    include_package_data=True,
    url="http://pypi.python.org/pypi/Lagring_v011/",
    license="MIT",
    description="Asset storage for Flask",
    long_description=open("README.txt").read(),
    install_requires=[
        "flask",
    ],
    extras_require = {
        'Pillow': []
    }
)