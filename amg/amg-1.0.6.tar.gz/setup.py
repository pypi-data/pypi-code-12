from setuptools import setup, find_packages
from const import VERSION


setup(
    name='amg',
    version=VERSION,
    py_modules=['amg', 'const'],
    author='zewait',
    author_email='wait@h4fan.com',
    description='app manager tool',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'jsonschema'
    ],
    entry_points={
        'console_scripts': [
            'amg = amg:main'
        ]
    }
)
