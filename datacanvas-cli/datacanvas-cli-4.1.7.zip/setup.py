from setuptools import setup,find_packages

PACKAGE = "ehccli"
NAME = "datacanvas-cli"
DESCRIPTION = "a simple datacavas-cli"
AUTHOR = "wc"
AUTHOR_EMAIL = "wangchang@zetyun.com"
setup(
    name=NAME,
    version='4.1.7',
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    packages = find_packages(),
    include_package_data = True,
    install_requires = ['requests','ConfigParser','argparse','prettytable'],
    entry_points={
        'console_scripts':[
            'datacanvas-cli = ehccli.ehcCli:main',
    ],
    }
)
