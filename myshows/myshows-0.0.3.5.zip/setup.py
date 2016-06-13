from setuptools import setup, find_packages

def version(filename):
    from os import path
    from re import findall, MULTILINE
    base = path.dirname(__file__)
    absolute_path = path.join(base, filename)
    with open(absolute_path) as file:
        file_data = file.read()
        version = findall(r'^VERSION\s*=\s*[\'"](.+)[\'"]', file_data, MULTILINE)[0]
        return version

setup(
    name='myshows',
    version = version('myshows/api.py'),

    author='Alexander Basov',
    author_email='farestz@gmail.com',

    url='https://github.com/farestz/myshows-python3',
    description='This is a myshows.me Python API',

    packages=find_packages(),
    install_requires='requests>=2.8,<3.0',

    license='MIT License',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords='myshows.me api myshows shows'
)
