import os.path

from setuptools import setup

from setup_utils import parse_version, write_version_py


MAJOR = 0
MINOR = 2
MICRO = 0

IS_RELEASED = True


INSTALL_REQUIRES = [
    "attrs >= 15.2.0",
    "okonomiyaki == 0.14.0",
    "six >= 1.9.0"
]

EXTRAS_REQUIRE = {
    ':python_version=="2.7"': [
        'enum34',
    ],
}

PACKAGES = [
    "simplesat",
    "simplesat.constraints",
    "simplesat.constraints.tests",
    "simplesat.examples",
    "simplesat.sat",
    "simplesat.sat.policy",
    "simplesat.sat.tests",
    "simplesat.tests",
    "simplesat.test_data",
    "simplesat.utils",
    "simplesat.utils.tests",
]

PACKAGE_DATA = {
    "simplesat.tests": ["*.yaml"],
    "simplesat.test_data": ["indices/*.json"],
}


if __name__ == "__main__":
    version_file = os.path.join("simplesat", "_version.py")
    write_version_py(version_file, MAJOR, MINOR, MICRO, IS_RELEASED)
    version = parse_version(version_file)

    setup(
        name='simplesat',
        version=version,
        author='Enthought, Inc',
        author_email='info@enthought.com',
        url='https://github.com/enthought/sat-solvers',
        description='Simple SAT solvers for use in Enstaller',
        packages=PACKAGES,
        package_data=PACKAGE_DATA,
        install_requires=INSTALL_REQUIRES,
        extras_require=EXTRAS_REQUIRE,
    )
