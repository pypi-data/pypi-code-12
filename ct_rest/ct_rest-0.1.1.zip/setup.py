from setuptools import setup, find_packages

setup(
    name = 'ct_rest',
    version = '0.1.1',
    keywords = ('django', 'ctcloud', 'rest', 'ct_rest', 'chinatelecom'),
    description = 'a rest utils for ctcloud using Django',
    license = 'MIT License',
    install_requires = ['Django>=1.8'],

    author = 'astwyg',
    author_email = 'i@ysgh.net',
    
    packages = find_packages(),
    platforms = 'any',

    url = "https://github.com/astwyg/ct-rest",
)