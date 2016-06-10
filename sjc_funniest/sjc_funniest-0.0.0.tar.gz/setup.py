from setuptools import setup

# def readme():
#     with open('README.rst') as f:
#         return f.read()

setup(
    setup_requires=['pbr>=1.9', 'setuptools>=17.1'],
    setup_cfg=True,
    pbr=True,
    install_requires=[
        'markdown'
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
    include_package_data=True,
    zip_safe=False
)
