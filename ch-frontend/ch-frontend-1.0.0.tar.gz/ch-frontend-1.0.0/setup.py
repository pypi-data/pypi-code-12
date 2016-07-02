import os, json
from distutils.core import setup

package = json.load(open("./package.json"))

setup(
        name = "ch-frontend",
        packages = ["ch-frontend"],
        package_dir = {"ch-frontend": "."},
        package_data = {
            "ch-frontend": [
                "dist/bootstrap/css/*.css",
                "dist/*.css",

                "dist/*.ico",
                "dist/*.gif",
                "dist/*.png",
                "dist/*.jpg",

                "dist/*.js",
                "data/*.json",
                "package.json"
            ]
        },
        version = package["version"],
        description = "PyPI package for frontend files",
        author = "Diwank Singh",
        author_email = "diwank.singh@gmail.com",
        url = "https://github.com/creatorrr/ch-frontend")

