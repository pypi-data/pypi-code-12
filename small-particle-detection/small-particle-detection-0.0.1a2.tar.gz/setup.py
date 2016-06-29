from distutils.core import setup

setup(
    name='small-particle-detection',
    version='0.0.1a2',
    packages=['spade', 'spade.shapes'],
    url='http://spade.gforge.inria.fr/',
    license='CeCILL',
    author='Nicolas Cedilnik',
    author_email='nicolas.cedilnik@inria.fr',
    description='Small Particle Detection, a shapes library-based object '
                'detector.',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Image Recognition',
        'License :: OSI Approved :: CEA CNRS Inria Logiciel Libre License, '
        'version 2.1 (CeCILL-2.1)',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='image, image processing, scientific research',
    install_requires=['numpy']
)
