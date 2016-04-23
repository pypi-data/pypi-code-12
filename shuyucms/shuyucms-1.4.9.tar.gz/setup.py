import os
import sys
from setuptools import setup, find_packages
from shutil import rmtree
from shuyucms import __version__ as version

exclude = ["shuyucms/project_template/dev.db",
           "shuyucms/project_template/local_settings.py"]
if sys.argv == ["setup.py", "test"]:
    exclude = []
exclude = dict([(e, None) for e in exclude])

for e in exclude:
    if e.endswith(".py"):
        try:
            os.remove("%sc" % e)
        except:
            pass
    try:
        with open(e, "r") as f:
            exclude[e] = (f.read(), os.stat(e))
        os.remove(e)
    except:
        pass

if sys.argv[:2] == ["setup.py", "bdist_wheel"]:
    # Remove previous build dir when creating a wheel build,
    # since if files have been removed from the project,
    # they'll still be cached in the build dir and end up
    # as part of the build, which is really neat!
    try:
        rmtree("build")
    except:
        pass

try:
    setup(
        name="shuyucms",
        version=version,
        author="Feichi LONG",
        author_email="feichi@longfeichi.com",
        description="ShuyuCMS is a powerful content management system abstracted from the project of zhidaoii.com, based on the Django Framework.",
        license="BSD",
        url="http://zhidaoii.com",
        zip_safe=False,
        include_package_data=True,
        packages=find_packages(),
        install_requires=[
            "django >1.6.0, <1.7.0",
            "syfilebrowser >=1.0",
            "wladmin >=1.0",
            "tzlocal >=1.0, <=1.2",
            "bleach >=1.4, <=1.4.2",
            "beautifulsoup4 >=4.1.3, <=4.4.0",
            "requests >=2.1.0",
            "requests-oauthlib >= 0.4",
            "future >= 0.9.0",
            "pillow",
        ],
        entry_points="""
            [console_scripts]
            shuyucms-project=shuyucms.bin.shuyucms_project:create_project
        """,
        test_suite="shuyucms.bin.runtests.main",
        tests_require=["pyflakes>=0.6.1", "pep8>=1.4.1"],
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Environment :: Web Environment",
            "Framework :: Django",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: BSD License",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2.6",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.3",
            "Topic :: Internet :: WWW/HTTP",
            "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
            "Topic :: Internet :: WWW/HTTP :: WSGI",
            "Topic :: Software Development :: Libraries :: "
            "Application Frameworks",
            "Topic :: Software Development :: Libraries :: Python Modules",
        ])
finally:
    for e in exclude:
        if exclude[e] is not None:
            data, stat = exclude[e]
            try:
                with open(e, "w") as f:
                    f.write(data)
                os.chown(e, stat.st_uid, stat.st_gid)
                os.chmod(e, stat.st_mode)
            except:
                pass
