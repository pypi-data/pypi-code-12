from setuptools import setup

setup(
    name="chunyun",
    version="0.9",
    description="A simple database migration tool",
    url="http://github.com/erhuabushuo/chunyun",
    author="疯人院主任",
    author_email="erhuabushuo@gmail.com",
    license="MIT",
    packages=['chunyun'],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'chunyun = chunyun.command_line:main'
        ]
    },
    test_suite='nose.collector',
    tests_require=['nose'],
)
