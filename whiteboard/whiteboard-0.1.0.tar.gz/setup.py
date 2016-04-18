from setuptools import setup
import ast
import re


_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('whiteboard/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))


with open('README.rst', 'r') as f:
    readme = f.read()


setup(
    name='whiteboard',
    version=version,
    url='https://github.com/nickfrostatx/flask-hookserver',
    author='Nick Frost',
    author_email='nickfrostatx@gmail.com',
    description='Take math notes in your browser',
    long_description=readme,
    packages=['whiteboard'],
    package_data={
        'whiteboard': [
            'static/*',
            'templates/*.html',
        ],
    },
    entry_points={
        'console_scripts': [
            'whiteboard = whiteboard.cli:run',
        ],
    },
    install_requires=[
        'click>=2.0',
        'Flask>=0.9',
        'Werkzeug>=0.7',
    ],
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Flask',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Text Editors',
    ],
)
