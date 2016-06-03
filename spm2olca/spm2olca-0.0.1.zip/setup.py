from setuptools import setup

setup(
    name="spm2olca",
    version="0.0.1",
    author="Michael Srocka",
    author_email="michael.srocka@gmail.com",
    description="SimaPro Method File to olca-schema converter",
    license="MIT",
    keywords="converter lca",
    url="https://github.com/GreenDelta/spm2olca",
    download_url='https://github.com/GreenDelta/spm2olca/tarball/v0.0.1',
    packages=['spm2olca'],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'spm2olca = spm2olca:main',
        ]
    },
    package_data={'spm2olca': ["data/*.*"]},
    long_description=open('README.rst').read(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.5",
        "Topic :: Utilities",
    ]
)
