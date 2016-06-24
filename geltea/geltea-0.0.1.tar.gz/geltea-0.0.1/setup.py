from setuptools import setup, find_packages

setup(
    name="geltea",   
    packages= find_packages(),
    license='MIT',
    author='Jelte Hoekstra',
    install_requires=['pandas', 'seaborn', 'sklearn', 'numpy', 'matplotlib'],
    version='0.0.1')
