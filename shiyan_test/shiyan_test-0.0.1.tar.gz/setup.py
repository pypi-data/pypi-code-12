from setuptools import setup, find_packages

setup(
    name = "shiyan_test",
    version = "0.0.1",
    keywords = ("pip", "shiyan", "test"),
    description = "shiyan test sdk",
    long_description = "shiyan test sdk for python",
    license = "MIT Licence",

    url = "http://yanyan.tech",
    author = "Yan Shi",
    author_email = "shiyanaimama@163.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = []
)
