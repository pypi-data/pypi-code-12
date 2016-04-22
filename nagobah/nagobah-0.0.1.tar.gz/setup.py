# _*_ coding: utf-8 _*_

"""setup script"""

from distutils.core import setup

setup(
        name="nagobah",
        py_modules=[
            "nagobah",
        ],
        author="xuanxuan",
        author_email="13060404095@163.com",
        version="0.0.1",
        url="https://github.com/littlegump/mydagobah.git",
        classifiers=[
            "Programming Language :: Python",
        ],
        entry_points={
            'console_scripts': [
                "nagobah = nagobah:main",
            ],
        },
)

