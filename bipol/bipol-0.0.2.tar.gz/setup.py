from setuptools import setup, find_packages

setup(
    name='bipol',
    version='0.0.2',
    description='A bipol plugin',
    author='Patrick Sanders',
    author_email='mail@patricksanders.net',
    install_requires=[
        'requests',
        'helga',
    ],
    packages=find_packages(),
    py_modules=['bipol'],
    include_package_data=True,
    zip_safe=True,
    entry_points=dict(
        helga_plugins=[
            'bipol = bipol:bipol',
        ],
    ),
)
