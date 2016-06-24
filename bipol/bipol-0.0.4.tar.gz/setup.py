from setuptools import setup, find_packages

setup(
    name='bipol',
    version='0.0.4',
    description='A bipol plugin',
    license='MIT',
    author='Patrick Sanders',
    author_email='mail@patricksanders.net',
    url='https://github.com/patricksanders/bipol',
    install_requires=[
        'requests',
        'helga',
    ],
    packages=find_packages(),
    py_modules=['bipol'],
    include_package_data=True,
    zip_safe=True,
    classifiers=[
        'License :: OSI Approved :: MIT License',
    ],
    entry_points=dict(
        helga_plugins=[
            'bipol = bipol:bipol',
        ],
    ),
)
