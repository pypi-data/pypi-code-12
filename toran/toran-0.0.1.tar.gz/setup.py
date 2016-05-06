from setuptools import setup, find_packages

setup(
    name='toran',
    version='0.0.1',
    description='Toran API server package',
    url='https://github.com/rvegas/python-toran.git',
    author='rvegas',
    author_email='info@ricardo.vegas',
    license='MIT',
    keywords='server api rest uwsgi toran',
    install_requires=['wsgiref', 'setuptools_git', 'requests', 'pyyaml'],
    dependency_links=[],
    package_dir={'': '.'},
    packages=find_packages(),
    exclude_package_data={'': ['.gitignore'], 'images': ['*.xcf', '*.blend']},
)
