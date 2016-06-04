from setuptools import setup, find_packages

setup(
    name = "system-status-server",
    version = '2.0.0',
    description = "This is a very lightweight stuff to get some system status info in JSON.",
    author = 'Lajos Santa',
    author_email = 'santa.lajos@coldline.hu',
    url = 'https://github.com/voidpp/system-status-server',
    license = 'MIT',
    install_requires = [
        "psutil==3.1.1",
        "Flask==0.11",
        "prettytable==0.7.2",
    ],
    packages = find_packages(),
    scripts = [
        "bin/hdd-stat",
    ],
)
