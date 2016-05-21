import os, json
from distutils.core import setup

package = json.load(open("./package.json"))

setup(
        name = package["name"],
        packages = [package["name"]],
        package_dir = {"ch-styles": "."},
        package_data = {
            "ch-styles": [
                "dist/css/bootstrap/*.map",
                "dist/css/bootstrap/*.css",

                "dist/assets/css/*.map",
                "dist/assets/css/*.css",

                "dist/assets/brand/*.ico",
                "dist/assets/brand/*.gif",
                "dist/assets/brand/*.png",
                "dist/assets/brand/*.jpg",

                "dist/assets/img/*.ico",
                "dist/assets/img/*.gif",
                "dist/assets/img/*.png",
                "dist/assets/img/*.jpg",

                "dist/assets/icons/*.svg",
                "dist/assets/flash/*.swf",

                "package.json",

                "fonts/*.eot",
                "fonts/*.svg",
                "fonts/*.ttf",
                "fonts/*.woff",
                "fonts/*.woff2"
            ]
        },
        version = package["version"],
        description = "PyPI package for style files",
        author = "Diwank Singh",
        author_email = "diwank.singh@gmail.com",
        url = "https://github.com/creatorrr/ch-styles-new")

