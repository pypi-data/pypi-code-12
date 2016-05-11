from setuptools import setup

setup(
    name='hsq',
    version='1.0',
    py_modules=['hsq'],
    package_data={'': ['carddefs.xq', 'hs.xq', 'hsq.xq']},
    include_package_data=True,
    author='Ed Kellett',
    zip_safe=False,
    install_requires=[
        'hearthstone',
    ],
    entry_points={
        'console_scripts': ['hsq = hsq:_main']
    }
)
