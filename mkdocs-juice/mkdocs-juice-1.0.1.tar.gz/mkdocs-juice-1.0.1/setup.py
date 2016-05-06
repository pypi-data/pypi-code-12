from setuptools import setup, find_packages

VERSION = '1.0.1'


setup(
    name="mkdocs-juice",
    version=VERSION,
    url='https://github.com/Dxtan/mkdocs-juice',
    license='MIT',
    description='This is a theme of mkdocs',
    author='Dxtan',
    author_email='dxtan@icloud.com',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'mkdocs.themes': [
            'juice = juice',
        ]
    },
    zip_safe=False
)
