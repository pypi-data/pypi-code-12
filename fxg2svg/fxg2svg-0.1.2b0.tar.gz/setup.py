from setuptools import setup, find_packages


EXCLUDE_FROM_PACKAGES = []

setup(
    name='fxg2svg',
    version='0.1.2b',
    description='FXG to SVG converter',
    url='https://bitbucket.org/suhain/fxg2svg',
    author='suhain',
    author_email='suhain93@gmail.com',
    license='MIT',
    packages=find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    install_requires=[
        'Pillow==3.2.0',
        'lxml==3.6.0',
    ],
    entry_points={
        'console_scripts': [
            'fxg2svg = fxg2svg.convert:main', 
        ]
    },
    classifiers=(
        b'Programming Language :: Python :: 3.4',
        b'Environment :: Console',
        b'Development Status :: 3 - Alpha',
        b'Intended Audience :: Developers',
        b'License :: OSI Approved :: MIT License',
    )
)
