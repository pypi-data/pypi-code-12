from setuptools import setup, find_packages
import heroin


setup(
    author="Anthony",
    name="heroin",
    version=heroin.__version__,
    packages=find_packages(exclude=["test*", ]),
    url="https://github.com/anthonyalmarza/heroin",
    description=(
        "`heroin`."
    ),
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    keywords=['heroin', ],
    install_requires=[
        'six', 'django', 'twisted'
    ],
    scripts=[
        'bin/heroin',
    ],
    extras_require={'dev': ['ipdb', 'mock', 'tox']},
    include_package_data=True
)
