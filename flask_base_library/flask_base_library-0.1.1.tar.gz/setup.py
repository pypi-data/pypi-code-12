from setuptools import setup

setup(
    name='flask_base_library',
    description='Flask base library for D Sanders',
    author='David Sanders',
    author_email='dsanderscanada@gmail.com',
    license='MIT',
    version='0.1.1',
    packages=[
        'flask_base_library',
        'flask_base_library.query_parameters',
        'flask_base_library.DateTimeEncoder'
    ]
)
