from distutils.core import setup

setup(
    name='SSKJpy',
    author="DefaltSimon",
    version='0.1.1',
    license='MIT',
    packages=["sskjpy"],
    description="A Slovenian dictionary parser written in python",
    long_description=open('README.txt').read(),
    install_requires=[
        "requests >= 2.9.1",
        "beautifulsoup4 >= 4.4.1",
    ],
)