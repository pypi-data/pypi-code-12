from setuptools import setup, find_packages

setup(
    name = "hdd-stat",
    description = "",
    version = "1.1.0",
    author = 'Lajos Santa',
    author_email = 'santa.lajos@coldline.hu',
    url = 'https://github.com/voidpp/hdd-stat',
    install_requires = [
        "prettytable==0.7.2",
        "psutil==4.1.0",
        "Flask==0.10.1",
    ],
    scripts = [
        "bin/hdd-stat"
    ],
    packages = find_packages(),
)

