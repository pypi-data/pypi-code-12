from setuptools import setup, find_packages
import molly


setup(
    author="Anthony",
    name="django-molly",
    version=molly.__version__,
    packages=find_packages(exclude=["test*", ]),
    url="https://github.com/anthonyalmarza/molly",
    description=(
        "`molly`."
    ),
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    keywords=['molly', ],
    install_requires=['six', 'django'],
    extras_require={'dev': ['ipdb', 'mock', 'twisted', 'heroin']},
    include_package_data=True
)
