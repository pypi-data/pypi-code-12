from setuptools import setup, find_packages

setup(
    name='hybrid',
    version='1.1.5',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires = [
        "tornado>=3.1.1",
        "flask",
        "DBUtils",
    ],
    entry_points={
        "console_scripts": [
            "hybrid = hybrid.commands:main",
        ],
    },

    author='timchow',
    author_email='jordan23nbastar@yeah.net',
    url='http://timd.cn/',
    description='hybrid tools set',
    keywords='hybrid server',
    license='LGPL',
)
