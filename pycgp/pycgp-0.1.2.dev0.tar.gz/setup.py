from setuptools import setup

descr = """Reader for GCP files in pure python.
pycgp is a pure pythen alternative to the wrapped GeometryReader that comes with
the CPG Software package available at:
http://hci.iwr.uni-heidelberg.de/MIP/Software/cgp.php
"""

DISTNAME            = 'pycgp'
DESCRIPTION         = 'Python reader for CGP files'
LONG_DESCRIPTION    = descr
MAINTAINER          = 'Tobias Maier'
MAINTAINER_EMAIL    = 'tobias.maier@unibas.ch'
URL                 = 'https://github.com/tobiasmaier/pycgp'
LICENSE             = 'BSD 3-clause'
DOWNLOAD_URL        = 'https://github.com/tobiasmaier/pycgp'
VERSION             = '0.1.2-dev'
PYTHON_VERSION      = (2, 7)
INST_DEPENDENCIES   = {}


if __name__ == '__main__':

    setup(name=DISTNAME,
        version=VERSION,
        url=URL,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        author=MAINTAINER,
        author_email=MAINTAINER_EMAIL,
        license=LICENSE,
        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Topic :: Scientific/Engineering',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX',
            'Operating System :: Unix',
            'Operating System :: MacOS',
        ],
        packages=['pycgp'],
        package_data={},
        install_requires=INST_DEPENDENCIES,
        scripts=[]
    )
