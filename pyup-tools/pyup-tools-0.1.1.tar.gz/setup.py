import setuptools

setuptools.setup(
    name="pyup-tools",
    version="0.1.1",
    url="https://github.com/pyupio/pyup-tools",

    author="pyup.io",
    author_email="support@pyup.io",

    description="Tools for pyup.io",
    long_description=open('README.md').read(),

    packages=setuptools.find_packages(),

    install_requires=[
        "click",
        "requests",
        "colorama"
    ],
    license="MIT",
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    entry_points={
        'console_scripts': [
            'pyup-tools = pyuptools.cli:cli',
        ]
    },
)
