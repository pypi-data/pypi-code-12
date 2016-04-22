# _*_ coding: utf-8 _*_

from distutils.core import setup

setup(
        name = "mydagobah",
        packages = [
            "mydagobah",
            ],
        version = "1.5.1",
        description = "expanded to dagobah, this is a script to import job in batch mode",
        author = "xuanxuan",
        author_email = "13060404095@163.com",
        url = "https:github.com/littlegump/mydagobah.git",
        keywords = ['dagobah', 'module_task', 'distribute hundreds of tasks'],
        classifiers = [
            "Programming Language :: Python",
            ],
        entry_points = {
            "console_scripts": [
                'dagopost = mydagobah.dagopost:run',
                ],
            }
        )

