#!/usr/bin/env python

from setuptools import setup
import versioneer

CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Science/Research",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: JavaScript",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 3",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: POSIX",
    "Operating System :: Unix",
    "Operating System :: MacOS",
]


if __name__ == '__main__':
    setup(
        name="juprog",
        author="Hai Nguyen",
        author_email="hainm.comp@gmail.com",
        description="Circular process for Jupyter notebook",
        version=versioneer.get_version(),
        cmdclass=versioneer.get_cmdclass(),
        classifiers=CLASSIFIERS,
        license="MIT",
        url="https://github.com/hainm/juprog",
        zip_safe=False,
        package_data={
            "juprog.progress-circle": ["*"],
        },
        packages=["juprog"],
        tests_require=["nose"],
        test_suite="nose.collector",
    )
