from distutils.core import setup

with open("requirements.txt", "r") as rf:
    reqs = [line.strip() for line in rf]

setup(
    name="thrivext",
    packages=["thrivext"],
    package_data={"thrivext": ["templates/*"]},
    include_package_data=True,
    version="0.0.6",
    install_requires=reqs,
    description="Thrivext: Thrive client extensions",
    author="Rohan Kekatpure",
    author_email="rohan_kekatpure@intuit.com",
    url="https://github.com/rohan-kekatpure/thrivext",
    download_url="https://github.com/rohan-kekatpure/thrivext/tarball/0.1",
    keywords=["pypi", "Thrive"],
    classifiers=[]
)