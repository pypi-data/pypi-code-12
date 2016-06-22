from setuptools import setup, find_packages

setup(
    name="kivish",
    description='html template language',
    version="0.2.0",
    packages=find_packages(),
    scripts=['kivish/scripts/kivish'],
    author='Jakub Ligęza',
    author_email='jakub.jaroslaw.ligeza@gmail.com',
    license='MIT',
    url='https://gitlab.com/jligeza/kivish',
)
